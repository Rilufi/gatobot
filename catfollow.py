import os
import requests
from typing import Dict, List

# Inicializando o cliente do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky

def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    print("Tentando autenticar no Bluesky...")
    resp = requests.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    print("Autenticação bem-sucedida.")
    return resp.json()

def search_pet_posts(pds_url: str, access_token: str, limit: int = 100) -> List[Dict]:
    """
    Procura por posts com mídia contendo fotos de gatos e cachorros no feed do usuário autenticado.
    """
    print("Buscando posts no feed do usuário autenticado...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept-Language": "en",  # Pode ajustar para múltiplos idiomas, se necessário
    }

    cursor = None
    pet_posts = []

    while True:
        params = {
            "limit": limit,
            "filter": "posts_with_media"
        }
        if cursor:
            params["cursor"] = cursor

        try:
            # Busca posts no timeline do usuário autenticado
            resp = requests.get(
                f"{pds_url}/xrpc/app.bsky.feed.getTimeline",
                headers=headers,
                params=params
            )
            resp.raise_for_status()
            feed_data = resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar o feed: {e}")
            break

        # Verifica se a resposta contém o campo "feed"
        if "feed" not in feed_data:
            print("A resposta da API não contém o campo 'feed'.")
            print("Resposta completa:", feed_data)
            break

        # Exibindo detalhes para depuração
        print("Posts recebidos para análise:", len(feed_data.get("feed", [])))
        
        # Filtra posts que mencionam gatos ou cachorros e possuem mídia
        for post in feed_data.get("feed", []):
            post_text = post.get("text", "").lower()
            media = post.get("embed", {}).get("images", [])

            print(f"Analisando post: {post_text}")
            print(f"Mídia associada: {media}")

            if (
                any(keyword in post_text for keyword in ["cat", "dog", "kitty", "puppy", "kitten", "#cat", "#dog", "#puppy", "#kitten"])
            ):
                pet_posts.append(post)

        # Verifica se há mais páginas para processar
        cursor = feed_data.get("cursor")
        if not cursor or len(pet_posts) >= limit:
            break

    if not pet_posts:
        print("Nenhum post com mídia de gatos ou cachorros foi encontrado.")
    else:
        print(f"Encontrados {len(pet_posts)} posts com mídia de gatos ou cachorros.")

    return pet_posts
def main():
    try:
        session = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)
        access_token = session.get("accessJwt")

        if not access_token:
            print("Token de acesso não encontrado.")
            return

        # Procura por posts de pets
        pet_posts = search_pet_posts(PDS_URL, access_token, limit=30)

        # Exibe os posts encontrados
        for post in pet_posts:
            print(f"Autor: {post.get('author', {}).get('displayName', 'Desconhecido')}")
            print(f"Texto: {post.get('text')}")
            print(f"Mídia: {post.get('embed', {}).get('images', [])}")
            print("-----\n")
    except Exception as e:
        print(f"Erro durante a execução: {e}")

if __name__ == "__main__":
    main()
