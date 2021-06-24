#! /usr/bin/env python
# coding=utf-8

import tweepy
from datetime import datetime, timezone, timedelta
import urllib.request
import os


#calling secret variables
CAT_KEY = os.environ.get("CAT_KEY")
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

#get the cats

site ="https://thiscatdoesnotexist.com/"
urllib.request.urlretrieve(site, 'fake_cat.jpeg')


#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')

#post on twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

mystring = f""" Gato Fake das {data}"""

#failsafe to try again in case the image is too large for twitter or any other problem
try:
	api.update_with_media('fake_cat.jpeg', mystring)
except:
	urllib.request.urlretrieve(site, 'fake_cat2.jpeg')
	api.update_with_media('fake_cat2.jpeg', mystring)

