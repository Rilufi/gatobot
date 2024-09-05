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

def get_pet_posts(api_client, author_did):
    pet_keywords = ["cat", "dog", "kitty", "puppy", "kitten", "#cat", "#dog", "#puppy", "#kitten"]
    pet_posts = []

    # Fetch posts with media using the filter parameter
    response = api_client.get_author_feed(
        actor=author_did,
        filter="posts_with_media"  # Fetch only posts with media
    )

    # Iterate over the posts and filter based on keywords
    for post in response['data']:
        post_text = post.get('text', '').lower()  # Assuming text is in a 'text' field

        # Check if any keyword is in the post text
        if any(keyword in post_text for keyword in pet_keywords):
            pet_posts.append(post)

    return pet_posts




def main():
    try:
        session = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)
        access_token = session.get("accessJwt")

        if not access_token:
            print("Token de acesso não encontrado.")
            return

        # Procura por posts de pets
        pet_posts = get_pet_posts(PDS_URL, access_token, limit=30)

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
