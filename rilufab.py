#! /usr/bin/env python
# coding=utf-8

import tweepy
#import os
#import random
from datetime import datetime, timezone, timedelta
import requests
import json
import urllib.request

url = "https://api.thecatapi.com/v1/images/search?format=json"

payload={}
headers = {
  'Content-Type': 'application/json',
  'x-api-key': '82dfc9d5-f821-4f67-b8ae-a4dd1af8671d'
}

proxies = {
  'http': 'http://10.10.1.10:3128',
}

response = requests.request("GET", url, headers=headers, data=payload, proxies=proxies)


#print(response.text)

todos = json.loads(response.text)


site = todos[0].get('url')


r = requests.get(site, allow_redirects=True)
 

open('gato.jpeg', 'wb').write(r.content)


fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')

consumer_key = 'RD04L1SMWeyNNx62v1tIW8Lof'
consumer_secret = 'BZG1fhoy3KKDRVjrxYjrBWjCsbaZQ6MtQYOEphQtkjqYlwbmMU'
access_token = '1375883846521065473-cfbZAMar1Fa5ygr8el1omyCLzk20Gb'
access_token_secret = 'OGCZYEsPMJ2GvGrwAjvIZCEpbtn6LN1WBqUWsRKTMijka'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAN46OAEAAAAAoQhvZsdmAd9x2vSFh%2Bsa9ThV8TQ%3DWo5GCUA3tg8kgPl3D4Qd9QzWKp0EPZBmhmYxTcw2CE8cTbrcaU'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


#path = r"/home/rilufab/data/cat/"
#random_cat = random.choice([
#    x for x in os.listdir(path)
#    if os.path.isfile(os.path.join(path, x))
#])
#print(random_cat)

mystring = f""" Gato Surpresa das {data}"""

try:
	api.update_with_media('gato.jpeg', mystring)
except:
	response2 = requests.request("GET", url, headers=headers, data=payload, proxies=proxies)
	todos2 = json.loads(response2.text)
	site2 = todos2[0].get('url')
	open('gato2.jpeg', 'wb').write(r2.content)
	api.update_with_media('gato2.jpeg', mystring)
