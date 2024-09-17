import os
from typing import Dict, List
import requests
from atproto import Client
import json
from datetime import datetime, timedelta, timezone
import time

# Configurações do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky
BOT_NAME = "Boturi"  # Nome do bot para evitar interagir com os próprios posts

# Limites diários e ações permitidas por hora
DAILY_LIMIT = 11666  # Limite de ações diárias
HOURLY_LIMIT = DAILY_LIMIT // 24  # Limite de ações por hora

# Arquivo para armazenar interações
INTERACTIONS_FILE = 'interactions.json'

def load_interactions():
    """Loads interactions from a JSON file."""
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"O arquivo {INTERACTIONS_FILE} está vazio ou corrompido. Inicializando com valores padrão.")
                return {"likes": [], "reposts": [], "follows": []}
    return {"likes": [], "reposts": [], "follows": []}

def save_interactions(interactions):
    """Saves interactions to a JSON file."""
    with open(INTERACTIONS_FILE, 'w') as file:
        json.dump(interactions, file)

def bsky_login_session(pds_url: str, handle: str, password: str) -> Client:
    """Logs in to Bluesky and returns the client instance."""
    print("Tentando autenticar no Bluesky...")
    client = Client(base_url=pds_url)
    client.login(handle, password)
    print("Autenticação bem-sucedida.")
    return client

def check_rate_limit(response):
    """Checks the rate limit status from the response headers and pauses if necessary."""
    rate_limit_remaining = int(response.headers.get('RateLimit-Remaining', 1))
    rate_limit_reset = int(response.headers.get('RateLimit-Reset', 0))

    if rate_limit_remaining <= 1:
        reset_time = datetime.fromtimestamp(rate_limit_reset, timezone.utc)
        current_time = datetime.now(timezone.utc)
        wait_seconds = (reset_time - current_time).total_seconds()
        print(f"Limite de requisições atingido. Aguardando {wait_seconds:.0f} segundos para o reset.")
        time.sleep(max(wait_seconds, 0))

def post_contains_hashtags(post: Dict, hashtags: List[str]) -> bool:
    """Verifica se o conteúdo do post contém alguma das hashtags especificadas e não contém hashtags a serem ignoradas."""
    content = post.get('record', {}).get('text', '').lower()
    
    # Hashtags a serem ignoradas
    ignored_hashtags = ['#furry', '#furryart']

    # Verifica se o post contém hashtags a serem ignoradas
    if any(ignored_hashtag in content for ignored_hashtag in ignored_hashtags):
        print(f"Post ignorado devido a hashtags bloqueadas: {ignored_hashtags}")
        return False

    # Verifica se contém as hashtags desejadas
    return any(hashtag.lower() in content for hashtag in hashtags)

def search_posts_by_hashtags(session: Client, hashtags: List[str], since: str, until: str) -> Dict:
    """Searches for posts containing the given hashtags within a specific time range."""
    cleaned_hashtags = [hashtag.replace('#', '').lower() for hashtag in hashtags]
    hashtag_query = " OR ".join(cleaned_hashtags)
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    headers = {"Authorization": f"Bearer {session._access_jwt}"}
    params = {
        "q": hashtag_query,
        "limit": 50,
        "since": since,
        "until": until,
        "sort": "latest"
    }

    response = requests.get(url, headers=headers, params=params)
    
    check_rate_limit(response)  # Checa e gerencia o limite de requisições
    
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Erro ao buscar posts para {hashtag_query}: {e}")
        print(f"Detalhes do erro: {response.text}")
        return {}

def find_images_with_keywords(post: Dict, keywords: List[str]) -> List[Dict]:
    """Finds images in the post that contain specified keywords in their 'alt' descriptions."""
    images_with_keywords = []
    embed = post.get('record', {}).get('embed')

    if embed and embed.get('$type') == 'app.bsky.embed.images':
        images = embed.get('images', [])
        for image in images:
            alt_text = image.get('alt', '').lower()
            if any(keyword in alt_text for keyword in keywords):
                images_with_keywords.append(image)

    return images_with_keywords

def like_post(client: Client, uri: str, cid: str, interactions):
    """Likes a post given its URI and CID, if not already liked."""
    if uri not in interactions["likes"]:
        client.like(uri=uri, cid=cid)
        interactions["likes"].append(uri)
        print(f"Post curtido: {uri}")

def repost_post(client: Client, uri: str, cid: str, interactions):
    """Reposts a post given its URI and CID, if not already reposted."""
    if uri not in interactions["reposts"]:
        client.repost(uri=uri, cid=cid)
        interactions["reposts"].append(uri)
        print(f"Post repostado: {uri}")

def follow_user(client: Client, did: str, interactions):
    """Follows a user given their DID, if not already followed."""
    if did not in interactions["follows"]:
        client.follow(did)
        interactions["follows"].append(did)
        print(f"Seguindo usuário: {did}")

if __name__ == "__main__":
    interactions = load_interactions()
    client = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)

    # Define hashtags e palavras-chave para busca
    hashtags = [
        "#cat", "#dog", "#gato", "#cachorro", 
        "#doglife", "#catvibes", "#catsofbluesky",
        "#dogsofbluesky", "#caturday"
    ]
    keywords = ['cat', 'dog', 'gato', 'cachorro']

    # Calcula as datas de ontem e hoje no formato ISO com timezone-aware completo
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    since = yesterday.isoformat()  # YYYY-MM-DDTHH:MM:SS+00:00
    until = today.isoformat()      # YYYY-MM-DDTHH:MM:SS+00:00

    actions_per_hour = HOURLY_LIMIT
    action_counter = 0

    # Busca posts dentro do intervalo de tempo especificado e valida hashtags e palavras-chave no alt text
    for hashtag in hashtags:
        try:
            search_results = search_posts_by_hashtags(client, [hashtag], since, until)
    
            print(f"Resultados da pesquisa para {hashtag}:")
            if not search_results.get('posts'):
                print("Nenhum resultado encontrado.")
            else:
                for post in search_results["posts"]:
                    uri = post.get('uri')
                    cid = post.get('cid')
                    author = post.get('author', {})
                    author_name = author.get('displayName', 'Unknown')
                    author_did = author.get('did', '')
    
                    # Evita interagir com posts do próprio bot
                    if author_name == BOT_NAME:
                        continue
    
                    # Verifica se a hashtag está presente no texto do post e ignora posts bloqueados
                    if post_contains_hashtags(post, [hashtag]):
                        # Verifica se o alt text das imagens contém as palavras-chave especificadas
                        images = find_images_with_keywords(post, keywords)
                        if images:
                            print(f"Post contém hashtag e palavras-chave no alt text: {uri}")
                            if action_counter < actions_per_hour:
                                # Curtir, repostar e seguir o autor do post se ainda não interagido
                                like_post(client, uri, cid, interactions)
                                action_counter += 1
                            if action_counter < actions_per_hour:
                                repost_post(client, uri, cid, interactions)
                                action_counter += 1
                            if action_counter < actions_per_hour:
                                follow_user(client, author_did, interactions)
                                action_counter += 1

                    if action_counter >= actions_per_hour:
                        print("Limite de ações por hora atingido.")
                        break
    
            if action_counter >= actions_per_hour:
                break
        except requests.exceptions.HTTPError as e:
            print(f"Erro ao buscar posts para {hashtag}: {e}")
    
    save_interactions(interactions)
    print("Concluído.")
