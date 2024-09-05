import os
from typing import Dict, List

from atproto import Client

# Assuming your Bluesky credentials are stored in environment variables
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")
PDS_URL = "https://bsky.social"

def create_atproto_client():
  """Cria um cliente atproto para interagir com a API do Bluesky."""
  client = Client(base_url=PDS_URL)
  client.login(BSKY_HANDLE, BSKY_PASSWORD)
  return client

def get_pet_posts(api_client: Client, author_did: str) -> List[Dict]:
    """
    Busca posts com imagens de gatos e/ou cachorros na rede social Bluesky.
    """
    pet_keywords = ["cat", "dog", "kitty", "puppy", "kitten", "#cat", "#dog", "#puppy", "#kitten"]
    pet_posts = []

    try:
        # Fetch posts with media using the get_author_feed method
        response = api_client.app.bsky.feed.get_author_feed(
            actor=author_did,
            filter="posts_with_media"
        )
        data = response.data  # Assuming the response structure aligns with the documentation
    except Exception as e:
        print(f"Erro ao buscar posts: {e}")
        return []

    # Iterate over the posts and filter based on keywords
    for post in data:
        post_text = post.get('text', '').lower()

        # Check if any keyword is in the post text
        if any(keyword in post_text for keyword in pet_keywords):
            pet_posts.append(post)

    return pet_posts


def main():
    try:
        # Cria um cliente atproto
        client = create_atproto_client()

        # Procura por posts de pets
        pet_posts = get_pet_posts(client, client.session.access_jwt)

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
