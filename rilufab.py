#! /usr/bin/env python
# coding=utf-8

import tweepy
from datetime import datetime, timezone, timedelta
import requests
import json
import urllib.request
import os

#calling secret variables
CAT_KEY = os.environ.get("CAT_KEY")
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

#get the cats
url = "https://api.thecatapi.com/v1/images/search?format=json"

payload={}
headers = {
  'Content-Type': 'application/json',
  'x-api-key': CAT_KEY
}

proxies = {
  'http': 'http://10.10.1.10:3128',
}


response = requests.request("GET", url, headers=headers, data=payload, proxies=proxies)
todos = json.loads(response.text)
site = todos[0].get('url')
r = requests.get(site, allow_redirects=True)
open('gato.jpeg', 'wb').write(r.content)

#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')

#post on twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

print(response.text)
print(CONSUMER_KEY)
print(CAT_KEY)

mystring = f""" Gato Surpresa das {data}"""

#failsafe to try again in case the image is too large for twitter or any other problem
#try:
#	api.update_with_media('gato.jpeg', mystring)
#except:
#	response2 = requests.request("GET", url, headers=headers, data=payload, proxies=proxies)
#	todos2 = json.loads(response2.text)
#	site2 = todos2[0].get('url')
#	r2 = requests.get(site2, allow_redirects=True)
#	open('gato2.jpeg', 'wb').write(r2.content)
#	api.update_with_media('gato2.jpeg', mystring)
