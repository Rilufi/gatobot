import tweepy
from datetime import datetime, timezone, timedelta
import requests
import json
import urllib.request
import os
from auth import api, client


#calling secret variables
CAT_KEY = os.environ.get("CAT_KEY")

#get the cats
url = "https://api.thecatapi.com/v1/images/search?format=json"

payload={}
headers = {
  'Content-Type': 'application/json',
  'x-api-key': CAT_KEY,
  "width":1600,"height":900,
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

mystring = f""" {data} Surprise Cat
#CatsOfTwitter #cats #CatsOnTwitter"""

#failsafe to try again in case the image is too large for twitter or any other problem
try:
	media = api.media_upload("gato.jpeg")
	client.create_tweet(text=mystring, media_ids=[media.media_id])
except:
	print("deu ruim o gato surpresa")
