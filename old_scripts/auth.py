import tweepy
import os

client = tweepy.Client(
    consumer_key = os.environ.get("CONSUMER_KEY"),
    consumer_secret = os.environ.get("CONSUMER_SECRET"),
    access_token = os.environ.get("ACCESS_TOKEN"),
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET"),
    wait_on_rate_limit=False
)

#calling secret variables
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

#connect on twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=False)
