import os
import requests
import json
import random
import urllib.request
from PIL import Image
import google.generativeai as genai
from typing import Dict, List, Tuple
from datetime import datetime, timezone, timedelta
import time
import tweepy
import sys
import requests.exceptions


#Autenticações twitter
consumer_key=os.environ.get("CONSUMER_KEY")
consumer_secret=os.environ.get("CONSUMER_SECRET")
access_token=os.environ.get("ACCESS_TOKEN")
access_token_secret=os.environ.get("ACCESS_TOKEN_SECRET")

# Autenticação via Tweepy API v2 (Client)
try:
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=False
    )
except Exception as e:
    print(f"Deu erro: {e}. Encerrando o script.")
    sys.exit(0)

# Autenticação via Tweepy API v1.1 (API)
try:
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=False)
except Exception as e:
    print(f"Deu erro: {e}. Encerrando o script.")
    sys.exit(0)

# Função para dividir o texto em partes menores sem cortar palavras
def get_chunks(text, max_length):
    words = text.split(' ')
    chunk = ''
    for word in words:
        if len(chunk) + len(word) + 1 <= max_length:
            chunk += ' ' + word if chunk else word
        else:
            yield chunk
            chunk = word
    if chunk:
        yield chunk

# Função para postar tweets com ou sem respostas
def post_tweet_with_replies(text, max_length=280):
    if len(text) <= max_length:
        # Postar o tweet diretamente se estiver dentro do limite de caracteres
        client.create_tweet(text=text)
    else:
        # Dividir o texto em partes menores
        chunks = get_chunks(text, max_length)
        # Postar o primeiro pedaço
        response = client.create_tweet(text=next(chunks))
        # Salvar o ID do primeiro tweet para responder a ele
        reply_to_id = response.data['id']
        # Postar os pedaços subsequentes como respostas
        for chunk in chunks:
            response = client.create_tweet(text=chunk, in_reply_to_tweet_id=reply_to_id)
            # Atualizar o ID para a próxima resposta
            reply_to_id = response.data['id']

# Exemplo de postagem com mídia usando API v1.1 para upload de imagem e API v2 para criar o tweet
def post_tweet_with_media(text, media_path):
    # Fazer upload da imagem via API v1.1
    media = api.media_upload(media_path)
    
    # Postar o tweet com a imagem via API v2
    client.create_tweet(text=text, media_ids=[media.media_id])

# Tudo do Bluesky daqui pra frente, sem precisar do pacote atpro (ou algo assim)
# Função para dividir texto em chunks
def split_text(text: str, max_length: int = 300) -> List[str]:
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += (word if current_chunk == "" else " " + word)
        else:
            chunks.append(current_chunk)
            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

# Função para tentar novamente com backoff exponencial em caso de erro 429
def retry_request(func, *args, **kwargs):
    max_retries = 5
    delay = 5
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Too many requests. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise
    raise Exception("Exceeded maximum retry attempts")

def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    response = retry_request(requests.post, pds_url + "/xrpc/com.atproto.server.createSession", json={"identifier": handle, "password": password})
    data = response.json()
    if "accessJwt" not in data:
        raise ValueError("Falha no login: accessJwt não encontrado na resposta")
    return data


def upload_file(pds_url: str, access_token: str, filename: str, img_bytes: bytes) -> Dict:
    suffix = filename.split(".")[-1].lower()
    mimetype = "application/octet-stream"
    if suffix in ["png"]:
        mimetype = "image/png"
    elif suffix in ["jpeg", "jpg"]:
        mimetype = "image/jpeg"
    elif suffix in ["webp"]:
        mimetype = "image/webp"

    resp = requests.post(
        pds_url + "/xrpc/com.atproto.repo.uploadBlob",
        headers={
            "Content-Type": mimetype,
            "Authorization": "Bearer " + access_token,
        },
        data=img_bytes,
    )
    resp.raise_for_status()
    return resp.json()["blob"]


def upload_image(pds_url: str, access_token: str, image_path: str, alt_text: str) -> Dict:
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    if len(img_bytes) > 1000000:
        raise Exception(f"Imagem muito grande. Máximo permitido é 1000000 bytes, obtido: {len(img_bytes)}")

    blob = upload_file(pds_url, access_token, image_path, img_bytes)
    return {
        "$type": "app.bsky.embed.images",
        "images": [{"alt": alt_text or "", "image": blob}],
    }

# Função para criar facets de reply (respostas)
def get_reply_refs(pds_url: str, parent_uri: str) -> Dict:
    try:
        repo, collection, rkey = parent_uri.split("/")[2:5]
        resp = retry_request(
            requests.get,
            pds_url + "/xrpc/com.atproto.repo.getRecord",
            params={"repo": repo, "collection": collection, "rkey": rkey},
        )
        parent = resp.json()
        parent_reply = parent["value"].get("reply")

        if parent_reply:
            return {
                "root": parent_reply["root"],
                "parent": {"uri": parent["uri"], "cid": parent["cid"]},
            }
        else:
            return {
                "root": {"uri": parent["uri"], "cid": parent["cid"]},
                "parent": {"uri": parent["uri"], "cid": parent["cid"]},
            }
    except Exception as e:
        print(f"Erro ao obter referências de reply: {e}")
        sys.exit(1)


def find_hashtags(text: str) -> List[Dict]:
    """
    Encontra hashtags no texto e retorna uma lista de facets para incluir no post.
    """
    facets = []
    words = text.split()
    byte_index = 0

    for word in words:
        if word.startswith("#"):
            start = byte_index
            end = byte_index + len(word)
            facets.append({
                "index": {
                    "byteStart": start,
                    "byteEnd": end
                },
                "features": [{
                    "$type": "app.bsky.richtext.facet#tag",
                    "tag": word[1:]  # Remove o '#' para a tag
                }]
            })
        byte_index += len(word) + 1  # +1 para o espaço após a palavra

    return facets

# Atualiza funções de postagem para usar o backoff exponencial
def post_chunk(pds_url: str, access_token: str, did: str, text: str, reply_to: Dict = None, embed: Dict = None) -> Tuple[str, str]:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    facets = find_hashtags(text)
    post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
        "facets": facets if facets else []  # Inclui facets se houver hashtags
    }

    if reply_to:
        post["reply"] = reply_to

    if embed:
        post["embed"] = embed

    # Usar retry com backoff exponencial para a postagem
    response = retry_request(requests.post, pds_url + "/xrpc/com.atproto.repo.createRecord",
                             headers={"Authorization": "Bearer " + access_token},
                             json={"repo": did, "collection": "app.bsky.feed.post", "record": post})
    
    return response.json()["uri"], response.json()["cid"]

# Function to post the cat fact on Bluesky
def post_bk(text: str):
    session = bsky_login_session(pds_url, handle, password)
    access_token = session["accessJwt"]
    did = session["did"]

    # Directly post the text without splitting into chunks or using replies
    post_chunk(pds_url, access_token, did, text)
    

def post_thread_with_image(pds_url: str, handle: str, password: str, long_text: str, image_path: str, alt_text: str):
    session = bsky_login_session(pds_url, handle, password)
    access_token = session["accessJwt"]
    did = session["did"]

    # Corta o texto em chunks
    chunks = split_text(long_text)
    
    # Posta o primeiro chunk com a imagem
    embed = upload_image(pds_url, access_token, image_path, alt_text)
    uri, cid = post_chunk(pds_url, access_token, did, chunks[0], embed=embed)

    # Posta o restante dos chunks como thread
    reply_to = get_reply_refs(pds_url, uri)

    for chunk in chunks[1:]:
        uri, cid = post_chunk(pds_url, access_token, did, chunk, reply_to)
        reply_to = get_reply_refs(pds_url, uri)

    print("Thread com imagem postada com sucesso!")

# Function to resize image for Bluesky
def resize_bluesky(image_path, max_file_size=1 * 1024 * 1024):
    """
    Redimensiona e comprime uma imagem para ficar dentro do limite de tamanho aceito pela rede social Bluesky.
    Substitui a imagem original se necessário.

    :param image_path: Caminho da imagem original.
    :param max_file_size: Tamanho máximo permitido da imagem em bytes (default: 1 MB).
    """
    # Abre a imagem usando o Pillow
    img = Image.open(image_path)

    # Redimensiona a imagem mantendo a proporção se necessário
    if os.path.getsize(image_path) > max_file_size:
        # Define o tamanho máximo para redimensionar
        img.thumbnail((1600, 1600))  # Redimensiona para caber dentro de 1600x1600 pixels

        # Reduz a qualidade gradualmente para atingir o tamanho desejado
        quality = 95
        while os.path.getsize(image_path) > max_file_size and quality > 10:
            img.save(image_path, quality=quality)
            quality -= 5
            img = Image.open(image_path)  # Recarrega a imagem para verificar o tamanho

        print(f"Imagem redimensionada e comprimida para o limite do Bluesky de {max_file_size} bytes.")
    else:
        img.save(image_path)
        print("Imagem já está dentro do limite de tamanho do Bluesky.")

def resize_twitter(image_path, max_file_size=5 * 1024 * 1024):
    """
    Redimensiona e comprime uma imagem para ficar dentro do limite de tamanho aceito pela rede social Bluesky.
    Substitui a imagem original se necessário.

    :param image_path: Caminho da imagem original.
    :param max_file_size: Tamanho máximo permitido da imagem em bytes (default: 1 MB).
    """
    # Abre a imagem usando o Pillow
    img = Image.open(image_path)

    # Redimensiona a imagem mantendo a proporção se necessário
    if os.path.getsize(image_path) > max_file_size:
        # Define o tamanho máximo para redimensionar
        img.thumbnail((1600, 1600))  # Redimensiona para caber dentro de 1600x1600 pixels

        # Reduz a qualidade gradualmente para atingir o tamanho desejado
        quality = 95
        while os.path.getsize(image_path) > max_file_size and quality > 10:
            img.save(image_path, quality=quality)
            quality -= 5
            img = Image.open(image_path)  # Recarrega a imagem para verificar o tamanho

        print(f"Imagem redimensionada e comprimida para o limite do Bluesky de {max_file_size} bytes.")
    else:
        img.save(image_path)
        print("Imagem já está dentro do limite de tamanho do Bluesky.")

# Inicializando api do Gemini
GOOGLE_API_KEY=os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def gemini_image(prompt, image_path):
    # Carregando a imagem
    imagem = Image.open(image_path)

    # Convertendo a imagem para o modo 'RGB' caso esteja em modo 'P'
    if imagem.mode == 'P':
        imagem = imagem.convert('RGB')

    # Gerando conteúdo com base na imagem e no prompt
    response = model.generate_content([prompt, imagem], stream=True)

    # Aguarda a conclusão da iteração antes de acessar os candidatos
    response.resolve()

    # Verificando a resposta
    if response.candidates and len(response.candidates) > 0:
        if response.candidates[0].content.parts and len(response.candidates[0].content.parts) > 0:
            text = response.candidates[0].content.parts[0].text

            # Supondo que o alt-text esteja separado por "ALT-TEXT:" na resposta
            if "ALT-TEXT:" in text:
                parts = text.split("ALT-TEXT:")
                legenda = parts[0].strip() if len(parts) > 0 else None
                alt_text = parts[1].strip() if len(parts) > 1 else None
                return legenda, alt_text
            else:
                print("Texto alternativo não encontrado.")
                return None
    print("Nenhum candidato válido encontrado.")
    return None


# Funções para pegar as imagens e postar
# Function to get random cat image and resize it if needed
def get_random_cat():
    CAT_KEY = os.environ.get("CAT_KEY")
    url = "https://api.thecatapi.com/v1/images/search?format=json"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': CAT_KEY,
    }
    response = requests.get(url, headers=headers)
    todos = json.loads(response.text)
    site = todos[0].get('url')
    r = requests.get(site, allow_redirects=True)
    
    # Open the downloaded image
    with open('cat_image.jpg', 'wb') as f:
        f.write(r.content)

# Function to get random dog image
def get_random_dog():
    DOG_KEY = os.environ.get("DOG_KEY")
    url = "https://api.thedogapi.com/v1/images/search?format=json"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': DOG_KEY,
    }
    response = requests.get(url, headers=headers)
    todos = json.loads(response.text)
    site = todos[0].get('url')
    r = requests.get(site, allow_redirects=True)
    
    # Open the downloaded image
    with open('dog_image.jpg', 'wb') as f:
        f.write(r.content)

# Function to download a random image
def download_random_image():
    # Generate random numbers for image URL
    w = random.randint(1, 6)
    x = random.randint(1, 9)
    y = random.randint(0, 9)
    z = random.randint(0, 9)

    # Construct image URL
    image_url = f"https://d2ph5fj80uercy.cloudfront.net/0{w}/cat{x}{y}{z}.jpg"

    # Make HTTP request to download image
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the image locally
        filename = "fakecat.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded image: {filename}")
    else:
        print("Error downloading image.")

# Function to post AI-generated cat skeet
def post_ai_generated_cat():
    response_gemini, alt_text = gemini_image(
        "Write a single funny and/or cute subtitle for a social media post (maximum 280 characters) about this AI-generated cat image with hashtags without explanations or introductions and create a descriptive alt text. Separate the subtitle from the alt text with 'ALT-TEXT:'",
        "fakecat.jpg"
    )
    if response_gemini is None:
        pass
    else:
        print(response_gemini, alt_text)
        resize_bluesky("fakecat.jpg")
        post_thread_with_image(pds_url, handle, password, response_gemini, "fakecat.jpg", alt_text)
        resize_twitter("fakecat.jpg")
        post_tweet_with_media(response_gemini, "fakecat.jpg")
    
# Function to post random cat skeet
def post_random_cat():
    response_gemini, alt_text = gemini_image(
        "Write a single funny and/or cute subtitle for a social media post (maximum 280 characters) about this cat image with hashtags without explanations or introductions and create a descriptive alt text. Separate the subtitle from the alt text with 'ALT-TEXT:'",
        'cat_image.jpg'
    )
    if response_gemini is None:
        pass
    else:
        print(response_gemini, alt_text)
        resize_bluesky("cat_image.jpg")
        post_thread_with_image(pds_url, handle, password, response_gemini, "cat_image.jpg", alt_text)
        resize_twitter("cat_image.jpg")
        post_tweet_with_media(response_gemini, "cat_image.jpg")

# Function to post random dog skeet
def post_random_dog():
    response_gemini, alt_text = gemini_image(
        "Write a single funny and/or cute subtitle for a social media post (maximum 280 characters) about this dog image with hashtags without explanations or introductions and create a descriptive alt text. Separate the subtitle from the alt text with 'ALT-TEXT:'",
        'dog_image.jpg'
    )
    if response_gemini is None:
        pass
    else:
        print(response_gemini, alt_text)
        resize_bluesky("dog_image.jpg")
        post_thread_with_image(pds_url, handle, password, response_gemini, "dog_image.jpg", alt_text)
        resize_twitter("dog_image.jpg")
        post_tweet_with_media(response_gemini, "dog_image.jpg")

# Function to get a cat fact from catfact.ninja
def get_cat_fact():
    # Loop until a fact without the word "skins" is obtained and with <= 300 characters
    while True:
        r = requests.get('https://catfact.ninja/fact')
        data = r.json()
        fact = data["fact"]
        if "skins" not in fact and len(fact) <= 300:
            return fact

# Inicializando o cliente do Bluesky
handle = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
password = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
pds_url = "https://bsky.social"


# Variável de controle para rate limit
has_hit_rate_limit = False

# Função principal
def main():
    global has_hit_rate_limit
    
    # Verificação de rate limit
    if has_hit_rate_limit:
        print("Limitado pelo rate limit. Script pausado.")
        sys.exit(0)
    
    cat_fact = get_cat_fact()
    
    # Lista de funções de download
    downloads = [
        lambda: download_random_image(),
        get_random_dog,
        get_random_cat
    ]

    # Executa downloads e trata exceções
    for download in downloads:
        try:
            download()
        except Exception as e:
            print(f"An error occurred during download: {e}")
            pass
    
    # Lista de funções de postagem
    skeets = [
        lambda: post_bk(cat_fact),
        lambda: post_tweet_with_replies(cat_fact),
        post_ai_generated_cat,
        post_random_cat,
        post_random_dog
    ]

    # Executa postagens com verificação de rate limit
    for skeet in skeets:
        try:
            # Tenta executar a postagem
            skeet()
            time.sleep(5 * 60)  # Aguarda 5 minutos entre as postagens

        except requests.exceptions.HTTPError as e:
            # Verifica se o erro é um rate limit (status 429)
            if e.response.status_code == 429:
                has_hit_rate_limit = True
                print("Erro 429 detectado. Script encerrado devido ao rate limit.")
                sys.exit(0)
            else:
                # Para outros erros HTTP, re-levanta a exceção
                raise

        except Exception as e:
            print(f"An error occurred during posting: {e}")
            time.sleep(5 * 60)  # Aguarda 5 minutos antes de tentar o próximo post

if __name__ == "__main__":
    main()
