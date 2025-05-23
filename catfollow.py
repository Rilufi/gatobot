import os
from typing import Dict, List
import requests
from atproto import Client
from datetime import datetime, timedelta, timezone
import time
import base64

# Configurações do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky
BOT_NAME = "Boturi"  # Nome do bot para evitar interagir com os próprios posts

# Configurações do GitHub
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Token de acesso do GitHub
GITHUB_REPO = "Rilufi/gatobot"  # Substitua pelo seu usuário/repositório
GITHUB_FILE_PATH = "interactions.txt"  # Caminho do arquivo no repositório

# Limites diários e ações permitidas por hora
DAILY_LIMIT = 11666  # Limite de ações diárias
HOURLY_LIMIT = DAILY_LIMIT // 24  # Limite de ações por hora

# Lista de palavras-chave inapropriadas
ADULT_KEYWORDS = [
    "nsfw", "porn", "sex", "nude", "onlyfans", "adult", "explicit",
    "xxx", "nsfw18+", "hentai", "fuck", "dick", "pussy", "ass",
    "bdsm", "fetish", "cum", "cock", "blowjob", "sexy", "naughty"
]

# Lista de contas banidas (opcional)
BANNED_ACCOUNTS = []  # Adicione handles de contas problemáticas se necessário

def load_interactions():
    """Carrega interações do arquivo interactions.txt no GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = response.json().get("content", "")
        if content:
            decoded_content = base64.b64decode(content).decode("utf-8")
            return decoded_content.splitlines()
    elif response.status_code == 404:
        print(f"Arquivo {GITHUB_FILE_PATH} não encontrado no repositório. Inicializando com lista vazia.")
    else:
        print(f"Erro ao carregar interações: {response.status_code} - {response.text}")
    
    return []

def save_interactions(interactions):
    """Salva interações no arquivo interactions.txt no GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None
    
    content = "\n".join(interactions)
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    data = {
        "message": "Atualizando interações",
        "content": encoded_content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"Interações salvas no GitHub: {GITHUB_FILE_PATH}")
    else:
        print(f"Erro ao salvar interações: {response.status_code} - {response.text}")

def bsky_login_session(pds_url: str, handle: str, password: str) -> Client:
    """Autentica no Bluesky e retorna a instância do cliente."""
    print("Tentando autenticar no Bluesky...")
    client = Client(base_url=pds_url)
    client.login(handle, password)
    print("Autenticação bem-sucedida.")
    return client

def check_rate_limit(response):
    """Verifica o status do limite de requisições e pausa, se necessário."""
    rate_limit_remaining = int(response.headers.get('RateLimit-Remaining', 1))
    rate_limit_reset = int(response.headers.get('RateLimit-Reset', 0))

    if rate_limit_remaining <= 1:
        reset_time = datetime.fromtimestamp(rate_limit_reset, timezone.utc)
        current_time = datetime.now(timezone.utc)
        wait_seconds = (reset_time - current_time).total_seconds()
        if wait_seconds > 0:
            print(f"Limite de requisições atingido. Aguardando {wait_seconds:.0f} segundos para o reset.")
            time.sleep(wait_seconds)
        else:
            print("Limite de requisições atingido, mas o tempo de reset já passou.")

def post_contains_hashtags(post: Dict, hashtags: List[str]) -> bool:
    """Verifica se o conteúdo do post contém alguma das hashtags especificadas."""
    content = post.get('record', {}).get('text', '').lower()
    return any(hashtag.lower() in content for hashtag in hashtags)

def is_safe_content(post: Dict) -> bool:
    """Verifica se o conteúdo do post é seguro (não contém palavras adultas)."""
    content = post.get('record', {}).get('text', '').lower()
    return not any(keyword in content for keyword in ADULT_KEYWORDS)

def is_not_nsfw(post: Dict) -> bool:
    """Verifica se o post não está marcado como NSFW."""
    labels = post.get('labels', [])
    return not any(label.get('val', '').lower() == 'nsfw' for label in labels)

def is_legitimate_account(author: Dict) -> bool:
    """Verifica se a conta parece legítima (não adulta)."""
    handle = author.get('handle', '').lower()
    display_name = author.get('displayName', '').lower()
    description = author.get('description', '').lower()
    
    suspicious_keywords = ["nsfw", "adult", "onlyfans", "porn", "18+", "venda", "conteúdo adulto"]
    
    # Verifica se a conta está na lista de banidas
    if handle in BANNED_ACCOUNTS:
        return False
        
    return not any(keyword in display_name or keyword in description 
                  for keyword in suspicious_keywords)

def search_posts_by_hashtags(client: Client, hashtags: List[str], since: str, until: str) -> Dict:
    """Busca posts contendo as hashtags fornecidas dentro de um intervalo de tempo."""
    cleaned_hashtags = [hashtag.replace('#', '').lower() for hashtag in hashtags]
    hashtag_query = " OR ".join(cleaned_hashtags)
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchposts"
    
    access_jwt = client._session.access_jwt
    headers = {"Authorization": f"Bearer {access_jwt}"}
    
    params = {
        "q": hashtag_query,
        "limit": 50,
        "since": since,
        "until": until,
        "sort": "latest"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao buscar posts para {hashtag_query}: {response.status_code}")
            print(f"Detalhes do erro: {response.text}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return {}
        
def like_post_bluesky(client: Client, uri: str, cid: str, interactions):
    """Curtir um post no Bluesky."""
    if f"like:{uri}" not in interactions:
        client.like(uri=uri, cid=cid)
        interactions.append(f"like:{uri}")
        save_interactions(interactions)
        print(f"Post curtido no Bluesky: {uri}")
    else:
        print(f"Post já curtido anteriormente: {uri}")

def repost_post_bluesky(client: Client, uri: str, cid: str, interactions):
    """Repostar um post no Bluesky."""
    if f"repost:{uri}" not in interactions:
        client.repost(uri=uri, cid=cid)
        interactions.append(f"repost:{uri}")
        save_interactions(interactions)
        print(f"Post repostado no Bluesky: {uri}")
    else:
        print(f"Post já repostado anteriormente: {uri}")

if __name__ == "__main__":
    interactions = load_interactions()
    bsky_client = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)

    # Define hashtags para busca (gatos e cachorros)
    hashtags = ["#cat", "#dog", "#gato", "#cachorro", "#cats", "#dogs", "#kitty", "#puppy"]

    # Calcula o intervalo de tempo para busca
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    since = yesterday.isoformat()
    until = today.isoformat()

    actions_per_hour = HOURLY_LIMIT
    action_counter = 0

    # Interação no Bluesky
    for hashtag in hashtags:
        try:
            search_results = search_posts_by_hashtags(bsky_client, [hashtag], since, until)
            if not search_results.get('posts'):
                print(f"Nenhum resultado encontrado para {hashtag} no Bluesky.")
                continue
                
            for post in search_results["posts"]:
                uri = post.get('uri')
                cid = post.get('cid')
                author = post.get('author', {})
                
                # Verificações de segurança
                if (author.get('displayName', '') == BOT_NAME or 
                    not is_safe_content(post) or 
                    not is_not_nsfw(post) or 
                    not is_legitimate_account(author)):
                    print(f"Post filtrado como inapropriado: {uri}")
                    continue
                
                if post_contains_hashtags(post, [hashtag]):
                    if action_counter < actions_per_hour:
                        like_post_bluesky(bsky_client, uri, cid, interactions)
                        repost_post_bluesky(bsky_client, uri, cid, interactions)
                        action_counter += 2
                    
                    if action_counter >= actions_per_hour:
                        print("Limite de ações por hora atingido no Bluesky.")
                        break
                        
        except requests.exceptions.HTTPError as e:
            print(f"Erro ao buscar posts para {hashtag} no Bluesky: {e}")

    print("Concluído.")
