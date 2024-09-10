import os
from typing import Dict, List
import requests
from atproto import Client
import json
from datetime import datetime, timedelta

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

def search_posts_by_hashtags(session: Client, hashtags: List[str], since: str, until: str) -> Dict:
    """Searches for posts containing the given hashtags within a specific time range."""
    hashtag_query = " OR ".join(hashtags)
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    headers = {"Authorization": f"Bearer {session._access_jwt}"}  # Usando _access_jwt obtido do client
    params = {
        "q": hashtag_query,
        "limit": 50,  # Ajuste o limite conforme necessário
        "since": since,
        "until": until
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

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

    # Define hashtags para busca
    hashtags = [
        "#cat", "#dog", "#gato", "#cachorro", 
        "#doglife", "#catvibes", "#catsofbluesky",
        "#dogsofbluesky", "#caturday"
    ]

    # Calcula as datas de ontem e hoje no formato ISO
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    since = yesterday.isoformat()  # YYYY-MM-DD
    until = today.isoformat()  # YYYY-MM-DD

    actions_per_hour = HOURLY_LIMIT
    action_counter = 0

    # Busca posts dentro do intervalo de tempo especificado
    for hashtag in hashtags:
        search_results = search_posts_by_hashtags(client, [hashtag], since, until)
        
        # Print detalhado sobre os resultados da pesquisa
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

                # Encontra imagens com 'cat' ou 'dog' nas descrições alt
                images = find_images_with_keywords(post, ['cat', 'dog'])

                if images and action_counter < actions_per_hour:
                    print(f"Post URI: {uri}")
                    print(f"Post CID: {cid}")
                    print(f"Author: {author_name}")
                    for image in images:
                        print(f"Image ALT: {image['alt']}")
                        print(f"Image URL: {image.get('url', 'No URL')}")
                    print("-----\n")

                    # Curtir, repostar e seguir o autor do post se ainda não interagido
                    if action_counter < actions_per_hour:
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

    save_interactions(interactions)
    print("Concluído.")
