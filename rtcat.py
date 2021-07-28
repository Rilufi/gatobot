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


#search hashtag and RT
queries = ["#CatsOfTwitter"]
for tweet in tweepy.Cursor(api.search, q=queries).items(1):
    api.create_favorite(tweet.id)
    tweet.retweet()
    api.create_friendship(tweet.user.screen_name)
