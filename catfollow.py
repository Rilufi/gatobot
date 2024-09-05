import os
import requests
from typing import Dict, List

# Inicializando o cliente do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky

def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    resp = requests.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    return resp.json()

def search_pet_posts(pds_url: str, access_token: str, limit: int = 30) -> List[Dict]:
    """
    Procura por posts com mídia contendo fotos de gatos e cachorros no feed do usuário autenticado.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept-Language": "en",  # Pode ajustar para múltiplos idiomas, se necessário
    }

    # Busca posts no timeline do usuário autenticado
    resp = requests.get(
        f"{pds_url}/xrpc/app.bsky.feed.getTimeline",
        headers=headers,
        params={"limit": limit}
    )
    resp.raise_for_status()
    feed_data = resp.json()

    pet_posts = []

    for post in feed_data.get("feed", []):
        post_text = post.get("text", "").lower()
        media = post.get("embed", {}).get("images", [])

        # Filtra posts que mencionam gatos ou cachorros e possuem mídia
        if ("cat" in post_text or "dog" in post_text or "#cat" in post_text or "#dog" in post_text) and media:
            pet_posts.append(post)

    return pet_posts

def main():
    session = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)
    access_token = session["accessJwt"]

    # Procura por posts de pets
    pet_posts = search_pet_posts(PDS_URL, access_token, limit=30)

    # Exibe os posts encontrados
    for post in pet_posts:
        print(f"Autor: {post.get('author', {}).get('displayName', 'Desconhecido')}")
        print(f"Texto: {post.get('text')}")
        print(f"Mídia: {post.get('embed', {}).get('images', [])}")
        print("-----\n")

if __name__ == "__main__":
    main()
