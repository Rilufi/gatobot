import tweepy
import os
from auth import api

#search hashtag, RT, like and follow
#three filters: one for only RT the original tweet, other for just media content and last safe images
queries = ['#CatsOfTwitter', '#DogsOfTwitter', '#Caturday', '#CatsOnTwitter', '#DogsOnTwitter']


def rtquery(hash):
    for tweet in tweepy.Cursor(api.search, q=f"{hash} -filter:retweets -filter:replies filter:images filter:safe", result_type="recent").items(1):
        try:
            api.create_friendship(tweet.user.screen_name)
            api.create_favorite(tweet.id)
            tweet.retweet()
        except:
            pass
    
for query in queries:
    rtquery(query)
