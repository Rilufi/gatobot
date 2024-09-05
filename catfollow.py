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


def search_posts_by_hashtags(session: Dict, hashtags: List[str]) -> Dict:
    """Searches for posts containing the given hashtags

    Args:
        session (Dict): The Bluesky session data obtained from bsky_login_session
        hashtags (List[str]): A list of hashtags to search for (without the # symbol)

    Returns:
        Dict: A dictionary containing the search results
    """

    # Combine hashtags with OR operator for searching multiple terms
    hashtag_query = " OR ".join(hashtags)

    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}  # Use accessJwt key
    params = {"q": hashtag_query, "limit": 5}  # You can adjust the limit as needed

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    # Login to Bluesky
    session = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)

    # Define the hashtags to search for (without #)
    hashtags = [
    #    "#cat",
     #   "#dog",
      #  "#gato",
      #  "#cachorro",
      #  "#doglife",
      #  "#catvibes",
        "#catsofbluesky",
        "#dogsofbluesky"#,
      #  "#caturday"
    ]

    # Search for posts
    for hashtag in hashtags:    
        search_results = search_posts_by_hashtags(session, hashtag)
        
        # Print more detailed information about the search results
        print("Resultados da pesquisa:")
        if not search_results.get('posts'):
            print("Nenhum resultado encontrado.")
        else:
            for post in search_results["posts"]:
                print(post)
                print(f"Post uri: {post.get('uri')}")
                print(f"Post uri: {post.get('cid')}")
                print(f"Author: {post.get('author', {}).get('displayName', 'Unknown')}")
                print(f"Alt: {post.get('images'['alt']}")#, {}).get('text', 'No Text')}")
                print("-----\n")
