import os
import requests
from typing import Dict, List


# Initializing Bluesky client (using environment variables)
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky


def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    """Logs in to Bluesky and returns the session data

    Args:
        pds_url (str): The Bluesky PDS URL
        handle (str): The Bluesky user handle
        password (str): The Bluesky user password

    Returns:
        Dict: The Bluesky session data dictionary
    """

    print("Tentando autenticar no Bluesky...")
    resp = requests.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    print("Autenticação bem-sucedida.")
    return resp.json()


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
                author_name = post.get('author', {}).get('displayName', 'Unknown')
                
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
                else:
                    print("Nenhuma imagem relevante encontrada com 'cat' ou 'dog'.\n")
