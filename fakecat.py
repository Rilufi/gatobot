import tweepy
from datetime import datetime, timezone, timedelta
import urllib.request
import os
from auth import api

#get the cats
site ="https://thiscatdoesnotexist.com/"
urllib.request.urlretrieve(site, 'fake_cat.jpeg')

#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')

mystring = f""" {data} Fake Cat
#AI #GAN #thiscatdoesnotexist"""

#failsafe to try again in case the image is too large for twitter or any other problem
try:
	api.update_with_media('fake_cat.jpeg', mystring)
except:
	urllib.request.urlretrieve(site, 'fake_cat2.jpeg')
	api.update_with_media('fake_cat2.jpeg', mystring)
