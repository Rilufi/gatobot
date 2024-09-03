import tweepy
import os
import requests
import json
import random
import urllib.request
from datetime import datetime, timezone, timedelta
from auth import api, client
from PIL import Image
import google.generativeai as genai
from time import sleep
from typing import Dict, List, Tuple


# Inicializando o cliente do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky

# Tudo do Bluesky daqui pra frente, sem precisar do pacote atpro (ou algo assim)
def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    resp = requests.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    return resp.json()

def parse_uri(uri: str) -> Dict:
    # Função para analisar a URI, separando em partes relevantes
    repo, collection, rkey = uri.split("/")[2:5]
    return {"repo": repo, "collection": collection, "rkey": rkey}

def get_reply_refs(pds_url: str, parent_uri: str) -> Dict:
    uri_parts = parse_uri(parent_uri)
    resp = requests.get(
        pds_url + "/xrpc/com.atproto.repo.getRecord",
        params=uri_parts,
    )
    resp.raise_for_status()
    parent = resp.json()
    parent_reply = parent["value"].get("reply")

    # Retorna as referências corretas para o root e parent
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


def post_chunk(pds_url: str, access_token: str, did: str, text: str, reply_to: Dict = None, embed: Dict = None) -> Tuple[str, str]:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }

    if reply_to:
        post["reply"] = reply_to

    if embed:
        post["embed"] = embed

    resp = requests.post(
        pds_url + "/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + access_token},
        json={
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
    resp.raise_for_status()
    response_data = resp.json()
    return response_data["uri"], response_data["cid"]

def post_bk_with_replies(text: str):
    pds_url = "https://bsky.social"
    handle = BSKY_HANDLE
    password = BSKY_PASSWORD
    session = bsky_login_session(pds_url, handle, password)
    access_token = session["accessJwt"]
    did = session["did"]

    chunks = split_text(text)
    reply_to = None

    for chunk in chunks:
        uri, cid = post_chunk(pds_url, access_token, did, chunk, reply_to)
        reply_to = get_reply_refs(pds_url, uri)  # Atualiza a referência para a próxima parte do thread

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
            return response.candidates[0].content.parts[0].text
        else:
            print("Nenhuma parte de conteúdo encontrada na resposta.")
    else:
        print("Nenhum candidato válido encontrado.")
    

# Functions for posting tweets
def post_tweet_with_replies(text, max_length=280):
    if len(text) <= max_length:
        # Post the tweet directly if it's within the character limit
        client.create_tweet(text=text)
    else:
        # Cut the text into chunks without splitting words
        chunks = get_chunks(text, max_length)
        # Post the first chunk
        response = client.create_tweet(text=next(chunks))
        # Save the ID of the first tweet
        reply_to_id = response.data['id']
        # Post subsequent chunks as replies to the first tweet
        for chunk in chunks:
            response = client.create_tweet(text=chunk, in_reply_to_tweet_id=reply_to_id)
            # Update the ID for the next reply
            reply_to_id = response.data['id']

# Function to split text into chunks without splitting words
def get_chunks(s, max_length):
    start = 0
    end = 0
    while start + max_length < len(s) and end != -1:
        end = s.rfind(" ", start, start + max_length + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]

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
    
    # Open the image using Pillow
    img = Image.open('cat_image.jpg')

    # Check if image exceeds Twitter's size limit (5 MB)
    max_file_size = 5 * 1024 * 1024  # 5 MB in bytes
    if os.path.getsize('cat_image.jpg') > max_file_size:
        # Resize the image while maintaining aspect ratio
        img.thumbnail((1600, 1600))  # Resize the image to fit within 1600x1600 pixels

        # Save the resized image
        img.save('cat_image.jpg')

        print("Image resized to fit Twitter's size limit.")
    else:
        print("Image size is within Twitter's size limit.")

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
    
    # Open the image using Pillow
    img = Image.open('dog_image.jpg')

    # Check if image exceeds Twitter's size limit (5 MB)
    max_file_size = 5 * 1024 * 1024  # 5 MB in bytes
    if os.path.getsize('dog_image.jpg') > max_file_size:
        # Resize the image while maintaining aspect ratio
        img.thumbnail((1600, 1600))  # Resize the image to fit within 1600x1600 pixels

        # Save the resized image
        img.save('dog_image.jpg')

        print("Image resized to fit Twitter's size limit.")
    else:
        print("Image size is within Twitter's size limit.")

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

# Function to post AI-generated cat tweet
def post_ai_generated_cat_tweet():
    data = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
    response_gemini = gemini_image("Write a funny tweet rating this ai-generated cat image with twitter related hashtags","fakecat.jpg")
    if response_gemini == None:
        response_gemini = "#AI #GAN #thesecatsdonotexist"
    else:
        pass
    mystring = f""" {data} AI-generated Cat
{response_gemini}"""
    print(mystring)
    media = api.media_upload("fakecat.jpg")
    client.create_tweet(text=mystring, media_ids=[media.media_id])
    response_gemini = gemini_image("Write a funny tweet rating this ai-generated cat image without hashtags", "fakecat.jpg")
    if response_gemini == None:
        response_gemini = "HBFC - Hourly Bluesky Fake Cat"
    else:
        pass
    mystring = f"""{data} AI-generated Cat
{response_gemini}"""
    print(mystring)
    resize_bluesky("fakecat.jpg")
    post_thread_with_image(pds_url, handle, password, mystring, "fakecat.jpg", "AI-generated image of a cat.")
    
# Function to post random cat tweet
def post_random_cat_tweet():
    data = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
    response_gemini = gemini_image("Write a funny and/or cute tweet about this cat image with twitter related hashtags",'cat_image.jpg')
    if response_gemini == None:
        response_gemini = "#CatsOfTwitter #cats #CatsOnTwitter"
    else:
        pass
    mystring = f""" {data} Surprise Cat
{response_gemini}"""
    print(mystring)
    media = api.media_upload("cat_image.jpg")
    client.create_tweet(text=mystring, media_ids=[media.media_id])
    response_gemini = gemini_image("Write a funny and/or cute tweet about this cat image without hashtags",'cat_image.jpg')
    if response_gemini == None or response_gemini == '"':
        response_gemini = "HBC - Hourly Bluesky Cat"
    else:
        pass
    mystring = f"""{data} Surprise Cat
{response_gemini}"""
    print(mystring)
    resize_bluesky("cat_image.jpg")
    post_thread_with_image(pds_url, handle, password, mystring, "cat_image.jpg", "Cat Picture.")

# Function to post random dog tweet
def post_random_dog_tweet():
    data = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
    response_gemini = gemini_image("Write a funny and/or cute tweet about this dog image with twitter related hashtags",'dog_image.jpg')
    if response_gemini == None:
        response_gemini = "#DogsOfTwitter #dogs #DogsOnTwitter"
    else:
        pass
    mystring = f""" {data} Surprise Dog
{response_gemini}"""
    print(mystring)
    media = api.media_upload("dog_image.jpg")
    client.create_tweet(text=mystring, media_ids=[media.media_id])
    response_gemini = gemini_image("Write a funny and/or cute tweet about this dog image without hashtags",'dog_image.jpg')
    if response_gemini == None:
        response_gemini = "HBD - Hourly Bluesky Dog"
    else:
        pass
    mystring = f"""{data} Surprise Dog
{response_gemini}"""
    print(mystring)
    resize_bluesky("dog_image.jpg")
    post_thread_with_image(pds_url, handle, password, mystring, "dog_image.jpg", "Dog Picture.")

# Function to get a cat fact from catfact.ninja for twitter
def get_cat_fact():
    # Loop until a fact without the word "skins" is obtained
    while True:
        r = requests.get('https://catfact.ninja/fact')
        data = r.json()
        fact = data["fact"]
        length = data["length"]
        if "skins" not in fact:
            return fact


# Function to post random dog tweet if the hour is 12
def cattp():
    # Get current hour
    hora = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H')

    if hora == '12':
        #list of errors and cat or dog
        pet = ["cat", "dog"]
        error = [100,101,102,200,201,202,203,204,206,207,300,301,302,303,304,305,307,308,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,420,421,422,423,424,425,426,429,431,444,450,451,497,498,499,500,501,502,503,504,506,507,508,509,510,511,521,523,525,599]

        # Get random image from one of these sites and post
        site ="https://http."+random.choice(pet)+"/"+str(random.choice(error))+".jpg"
        urllib.request.urlretrieve(site, 'http_pet.jpg')
        mystring = f""" HTTP status of the day {datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%d/%m')}"""
        media = api.media_upload("http_pet.jpg")
        client.create_tweet(text=mystring, media_ids=[media.media_id])
    else:
        pass

def rate_status():
    # Get rate limit status
    response = api.rate_limit_status()

    # Check if the '/statuses/update' key exists in the response
    if '/statuses/update' not in response['resources']['statuses']:
        print("'/statuses/update' not found in rate limit status. Continuing script.")
    else:
        print("'/statuses/update' found in rate limit status. Exiting script.")
        exit()

pds_url = "https://bsky.social"
handle = BSKY_HANDLE
password = BSKY_PASSWORD

# Main function
def main():
    # Checking rate limit before doing anything else
    rate_status()
    
    # Call necessary functions
    download_random_image()
    get_random_dog()
    get_random_cat()
    cat_fact = get_cat_fact()
    
    # Posta tweets com pausas de 5 minutos
    tweets = [
        lambda: post_bk_with_replies(cat_fact),
	post_tweet_with_replies(cat_fact),
        post_ai_generated_cat_tweet,
        post_random_cat_tweet,
        post_random_dog_tweet,
        cattp
    ]

    for tweet in tweets:
        try:
            tweet()
        except Exception as e:
            print(f"An error occurred: {e}")
        sleep(300)

if __name__ == "__main__":
    main()
