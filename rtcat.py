#! /usr/bin/env python
# coding=utf-8

import tweepy
import os

#calling secret variables
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]


#connect on twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


#search hashtag, RT, like an follow
#in case I want more hashtags, I'll leave the queries list commented
#also put two filters, one for only RT the original tweet and other for just media content
#queries = ["#CatsOfTwitter -filter:retweets"]
for tweet in tweepy.Cursor(api.search, q="#CatsOfTwitter -filter:retweets filter:media").items(1):
    api.create_favorite(tweet.id)
    api.create_friendship(tweet.user.screen_name)
    tweet.retweet()
