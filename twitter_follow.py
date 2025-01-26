import os
from typing import Dict, List
import json
from datetime import datetime, timedelta, timezone
import tweepy
import sys

# Autenticações Twitter
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

# Verifica se as credenciais do Twitter estão definidas
if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    print("Credenciais do Twitter não encontradas. Verifique as variáveis de ambiente.")
    sys.exit(1)

# Autenticação via Tweepy API v2 (Client)
try:
    twitter_client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True
    )
    # Verifica se a autenticação foi bem-sucedida
    twitter_client.get_me()  # Testa a autenticação
    print("Autenticação no Twitter bem-sucedida.")
except tweepy.errors.Unauthorized as e:
    print(f"Erro de autenticação no Twitter: {e}. Verifique suas credenciais.")
    sys.exit(1)
except Exception as e:
    print(f"Erro inesperado na autenticação do Twitter: {e}")
    sys.exit(1)

# Autenticação via Tweepy API v1.1 (API)
try:
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
    # Verifica se a autenticação foi bem-sucedida
    twitter_api.verify_credentials()
    print("Autenticação no Twitter (API v1.1) bem-sucedida.")
except tweepy.errors.Unauthorized as e:
    print(f"Erro de autenticação no Twitter (API v1.1): {e}. Verifique suas credenciais.")
    sys.exit(1)
except Exception as e:
    print(f"Erro inesperado na autenticação do Twitter (API v1.1): {e}")
    sys.exit(1)

# Arquivo para armazenar interações
INTERACTIONS_FILE = 'twitter_interactions.json'

def load_interactions() -> Dict:
    """Carrega interações de um arquivo JSON."""
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"O arquivo {INTERACTIONS_FILE} está vazio ou corrompido. Inicializando com valores padrão.")
                return {"likes": [], "follows": []}
    return {"likes": [], "follows": []}

def save_interactions(interactions: Dict):
    """Salva interações em um arquivo JSON."""
    with open(INTERACTIONS_FILE, 'w') as file:
        json.dump(interactions, file)

def like_post_twitter(tweet_id: str, interactions):
    """Curtir um post no Twitter."""
    if tweet_id not in interactions["likes"]:
        try:
            twitter_client.like(tweet_id)
            interactions["likes"].append(tweet_id)
            print(f"Post curtido no Twitter: {tweet_id}")
        except tweepy.errors.TweepyException as e:
            print(f"Erro ao curtir o tweet {tweet_id}: {e}")

def follow_user_twitter(username: str, interactions):
    """Seguir um usuário no Twitter."""
    if username not in interactions["follows"]:
        try:
            twitter_api.create_friendship(screen_name=username)
            interactions["follows"].append(username)
            print(f"Seguindo usuário no Twitter: @{username}")
        except tweepy.errors.TweepyException as e:
            print(f"Erro ao seguir o usuário @{username}: {e}")

def search_tweets_by_hashtags(hashtags: List[str]):
    """Busca tweets contendo as hashtags fornecidas."""
    query = " OR ".join(hashtags)
    try:
        tweets = twitter_client.search_recent_tweets(query=query, max_results=50)
        return tweets.data if tweets.data else []
    except tweepy.errors.TweepyException as e:
        print(f"Erro ao buscar tweets: {e}")
        return []

if __name__ == "__main__":
    interactions = load_interactions()

    # Define hashtags e palavras-chave para busca
    hashtags = [
        "#cat", "#dog", "#gato", "#cachorro", 
        "#doglife", "#catvibes", "#catsofbluesky",
        "#dogsofbluesky", "#caturday"
    ]

    actions_per_hour = 50  # Limite de ações por hora
    action_counter = 0

    # Interação no Twitter
    tweets = search_tweets_by_hashtags(hashtags)
    for tweet in tweets:
        tweet_id = tweet.id
        username = tweet.author_id

        if action_counter < actions_per_hour:
            like_post_twitter(tweet_id, interactions)
            action_counter += 1
        if action_counter < actions_per_hour:
            follow_user_twitter(username, interactions)
            action_counter += 1

        if action_counter >= actions_per_hour:
            print("Limite de ações por hora atingido no Twitter.")
            break

    save_interactions(interactions)
    print("Concluído.")
