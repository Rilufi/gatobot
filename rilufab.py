#! /usr/bin/env python
# coding=utf-8

import tweepy
from datetime import datetime, timezone, timedelta
import requests
import json
import urllib.request

url = "https://api.thecatapi.com/v1/images/search?format=json"

payload={}
headers = {
  'Content-Type': 'application/json',
  'x-api-key': cat_key
}

proxies = {
  'http': 'http://10.10.1.10:3128',
}


response = requests.request("GET", url, headers=headers, data=payload, proxies=proxies)
todos = json.loads(response.text)
site = todos[0].get('url')
r = requests.get(site, allow_redirects=True)
open('gato.jpeg', 'wb').write(r.content)


fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


mystring = f""" Gato Surpresa das {data}"""

try:
	api.update_with_media('gato.jpeg', mystring)
except:
	response2 = requests.request("GET", url, headers=headers, data=payload, proxies=proxies)
	todos2 = json.loads(response2.text)
	site2 = todos2[0].get('url')
	open('gato2.jpeg', 'wb').write(r2.content)
	api.update_with_media('gato2.jpeg', mystring)
