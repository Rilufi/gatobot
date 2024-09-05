import os
import requests
from typing import Dict, List

# Initializing Bluesky client (using environment variables)
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky
BOT_NAME = "Boturi"  # Nome do bot para evitar interagir com os próprios posts

def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    """Logs in to Bluesky and returns the session data."""
    print("Tentando autenticar no Bluesky...")
    resp = requests.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    print("Autenticação bem-sucedida.")
    return resp.json()

def search_posts_by_hashtags(session: Dict, hashtags: List[str]) -> Dict:
    """Searches for posts containing the given hashtags."""
    hashtag_query = " OR ".join(hashtags)
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    params = {"q": hashtag_query, "limit": 5}  # Ajuste o limite conforme necessário

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def find_images_with_keywords(post: Dict, keywords: List[str]) -> List[Dict]:
    """Finds images in the post that contain specified keywords in their 'alt' descriptions."""
    images_with_keywords = []
    embed = post.get('record', {}).get('embed')
    
    # Check if the embed type is images
    if embed and embed.get('$type') == 'app.bsky.embed.images':
        images = embed.get('images', [])
        for image in images:
            alt_text = image.get('alt', '').lower()
            if any(keyword in alt_text for keyword in keywords):
                images_with_keywords.append(image)
                
    return images_with_keywords

def like_post(session: Dict, uri: str, cid: str):
    """Likes a post given its URI and CID."""
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.like"
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    data = {"uri": uri, "cid": cid}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Post curtido: {uri}")

def repost_post(session: Dict, uri: str, cid: str):
    """Reposts a post given its URI and CID."""
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.repost"
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    data = {"uri": uri, "cid": cid}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Post repostado: {uri}")

def follow_user(session: Dict, did: str):
    """Follows a user given their DID."""
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.follow"
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    data = {"did": did}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Seguindo usuário: {did}")

if __name__ == "__main__":
    # Login to Bluesky
    session = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)

    # Define the hashtags to search for (without #)
    hashtags = [
            "#cat",
            "#dog",
            "#gato",
            "#cachorro",
            "#doglife",
            "#catvibes",
            "#catsofbluesky",
            "#dogsofbluesky",
            "#caturday"
        ]

    # Search for posts
    for hashtag in hashtags:    
        search_results = search_posts_by_hashtags(session, [hashtag])
        
        # Print detailed information about the search results
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
                
                # Evitar interagir com posts do próprio bot
                if author_name == BOT_NAME:
                    continue

                # Find images containing 'cat' or 'dog' in their alt descriptions
                images = find_images_with_keywords(post, ['cat', 'dog'])
                
                if images:
                    print(f"Post URI: {uri}")
                    print(f"Post CID: {cid}")
                    print(f"Author: {author_name}")
                    for image in images:
                        print(f"Image ALT: {image['alt']}")
                        print(f"Image URL: {image.get('url', 'No URL')}")
                    print("-----\n")
                    
                    # Curtir, repostar e seguir o autor do post
                    like_post(session, uri, cid)
                    repost_post(session, uri, cid)
                    follow_user(session, author_did)
                else:
                    print("Nenhuma imagem relevante encontrada com 'cat' ou 'dog'.\n")
