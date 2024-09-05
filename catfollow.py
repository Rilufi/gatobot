import requests
import os

BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"
PET_KEYWORDS = ["cat", "dog", "gato", "cachorro", "kitty", "puppy", "kitten"]

# Autenticação
resp = requests.post(
    "https://bsky.social/xrpc/com.atproto.server.createSession",
    json={"identifier": BSKY_HANDLE, "password": BSKY_PASSWORD},
)
resp.raise_for_status()
session = resp.json()
access_token = session["accessJwt"]

# Buscar posts com imagens
headers = {"Authorization": f"Bearer {access_token}"}
params = {"filter": "posts_with_media"}

resp = requests.get(
    f"{PDS_URL}/xrpc/app.bsky.feed.getAuthorFeed",
    headers=headers,
    params=params
)
resp.raise_for_status()
feed = resp.json()["data"]

# Filtrar posts por palavras-chave relacionadas a pets
pet_posts = []
for post in feed:
    text = post.get("text", "").lower()
    if any(keyword in text for keyword in PET_KEYWORDS):
        pet_posts.append(post)

# Imprimir os posts encontrados
for post in pet_posts:
    print(f"Autor: {post.get('author', {}).get('displayName', 'Desconhecido')}")
    print(f"Texto: {post.get('text')}")
    print(f"Imagens: {post.get('embed', {}).get('images', [])}")
    print("-----\n")
