import tweepy
from datetime import datetime, timezone, timedelta
import urllib.request
import os
from auth import api, client
import requests
from bs4 import BeautifulSoup
import re


# HTML com as imagens
html_content = '''
<div class="row">
    <div class="column">
        <img id="1" style="width:100%" src="https://d2ph5fj80uercy.cloudfront.net/04/cat4267.jpg">
        <img id="2" style="width:100%" src="https://d2ph5fj80uercy.cloudfront.net/05/cat1704.jpg">
        <img id="3" style="width:100%" src="https://d2ph5fj80uercy.cloudfront.net/06/cat1224.jpg">
        <!-- mais imagens -->
    </div>
    <!-- outras colunas -->
</div>
'''

# Criar um objeto BeautifulSoup para analisar o HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Encontrar todas as imagens na página
all_images = soup.find_all('img')

# Encontrar a primeira imagem de gato
image_url = None
for img in all_images:
    if 'src' in img.attrs and 'https://d2ph5fj80uercy.cloudfront.net/' in img['src']:
        image_url = img['src']
        break

# Se uma imagem de gato foi encontrada, faça o download dela
if image_url:
    image_data = requests.get(image_url).content
    with open('cat_image.jpg', 'wb') as f:
        f.write(image_data)
    print("Imagem de gato salva com sucesso como 'cat_image.jpg'")
else:
    print("Nenhuma imagem de gato encontrada na página.")


#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')

mystring = f""" {data} AI Cat
#AI #GAN #thiscatdoesnotexist"""

#media = api.media_upload("cat_image.jpg")
#client.create_tweet(text=mystring, media_ids=[media.media_id]) 
