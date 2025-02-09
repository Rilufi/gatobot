import os
from typing import Dict, List
import requests
from atproto import Client
import json
from datetime import datetime, timedelta, timezone
import time
import sys

# Configurações do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky
BOT_NAME = "Boturi"  # Nome do bot para evitar interagir com os próprios posts

# Limites diários e ações permitidas por hora
DAILY_LIMIT = 11666  # Limite de ações diárias
HOURLY_LIMIT = DAILY_LIMIT // 24  # Limite de ações por hora

# Arquivo para armazenar interações
INTERACTIONS_FILE = 'bluesky_interactions.json'

def load_interactions() -> Dict:
    """Carrega interações de um arquivo JSON."""
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"O arquivo {INTERACTIONS_FILE} está vazio ou corrompido. Inicializando com valores padrão.")
                return {"likes": [], "follows": [], "unfollows": []}
    return {"likes": [], "follows": [], "unfollows": []}

def save_interactions(interactions: Dict):
    """Salva interações em um arquivo JSON."""
    with open(INTERACTIONS_FILE, 'w') as file:
        json.dump(interactions, file)

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
        print(f"Limite de requisições atingido. Aguardando {wait_seconds:.0f} segundos para o reset.")
        time.sleep(max(wait_seconds, 0))

def post_contains_hashtags(post: Dict, hashtags: List[str]) -> bool:
    """Verifica se o conteúdo do post contém alguma das hashtags especificadas."""
    content = post.get('record', {}).get('text', '').lower()
    return any(hashtag.lower() in content for hashtag in hashtags)

def search_posts_by_hashtags(session: Client, hashtags: List[str], since: str, until: str) -> Dict:
    """Busca posts contendo as hashtags fornecidas dentro de um intervalo de tempo."""
    cleaned_hashtags = [hashtag.replace('#', '').lower() for hashtag in hashtags]
    hashtag_query = " OR ".join(cleaned_hashtags)
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    
    # Obtém o token de acesso da sessão
    access_jwt = session._session.access_jwt
    headers = {"Authorization": f"Bearer {access_jwt}"}
    
    params = {
        "q": hashtag_query,
        "limit": 50,
        "since": since,
        "until": until,
        "sort": "latest"
    }

    response = requests.get(url, headers=headers, params=params)
    check_rate_limit(response)  # Verifica e gerencia o limite de requisições

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Erro ao buscar posts para {hashtag_query}: {e}")
        print(f"Detalhes do erro: {response.text}")
        return {}

def like_post_bluesky(client: Client, uri: str, cid: str, interactions):
    """Curtir um post no Bluesky."""
    if uri not in interactions["likes"]:
        client.like(uri=uri, cid=cid)
        interactions["likes"].append(uri)
        print(f"Post curtido no Bluesky: {uri}")

def follow_user_bluesky(client: Client, did: str, interactions):
    """Seguir um usuário no Bluesky."""
    if did not in interactions["follows"] and did not in interactions["unfollows"]:
        client.follow(did)
        interactions["follows"].append(did)
        print(f"Seguindo usuário no Bluesky: {did}")

def unfollow_user_bluesky(client: Client, did: str, interactions):
    """Deixar de seguir um usuário no Bluesky."""
    if did in interactions["follows"]:
        client.unfollow(did)
        interactions["follows"].remove(did)
        interactions["unfollows"].append(did)
        print(f"Deixando de seguir usuário no Bluesky: {did}")

if __name__ == "__main__":
    interactions = load_interactions()
    bsky_client = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)

    # Define hashtags e palavras-chave para busca
    hashtags = [
        "#cat", "#dog", "#gato", "#cachorro", 
        "#doglife", "#catvibes", "#catsofbluesky",
        "#dogsofbluesky", "#caturday"
    ]

    # Calcula as datas de ontem e hoje no formato ISO com timezone-aware completo
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    since = yesterday.isoformat()  # YYYY-MM-DDTHH:MM:SS+00:00
    until = today.isoformat()      # YYYY-MM-DDTHH:MM:SS+00:00

    actions_per_hour = HOURLY_LIMIT
    action_counter = 0

    # Interação no Bluesky
    for hashtag in hashtags:
        try:
            search_results = search_posts_by_hashtags(bsky_client, [hashtag], since, until)
            if not search_results.get('posts'):
                print(f"Nenhum resultado encontrado para {hashtag} no Bluesky.")
            else:
                for post in search_results["posts"]:
                    uri = post.get('uri')
                    cid = post.get('cid')
                    author = post.get('author', {})
                    author_did = author.get('did', '')

                    # Evita interagir com posts do próprio bot
                    if author.get('displayName', '') == BOT_NAME:
                        continue

                    if post_contains_hashtags(post, [hashtag]):
                        if action_counter < actions_per_hour:
                            like_post_bluesky(bsky_client, uri, cid, interactions)
                            action_counter += 1
                        if action_counter < actions_per_hour and author_did not in interactions["follows"] and author_did not in interactions["unfollows"]:
                            follow_user_bluesky(bsky_client, author_did, interactions)
                            action_counter += 1

                    if action_counter >= actions_per_hour:
                        print("Limite de ações por hora atingido no Bluesky.")
                        break
        except requests.exceptions.HTTPError as e:
            print(f"Erro ao buscar posts para {hashtag} no Bluesky: {e}")

    save_interactions(interactions)
    print("Concluído.")
