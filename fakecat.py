import tweepy
from datetime import datetime, timezone, timedelta
import urllib.request
import os
from auth import api, client
import requests
from bs4 import BeautifulSoup
import re


import re
import requests
from bs4 import BeautifulSoup

# URL da página
url = "https://thesecatsdonotexist.com/"

# Fazer a solicitação HTTP
response = requests.get(url)

# Verificar se a solicitação foi bem-sucedida
if response.status_code == 200:
    # Criar um objeto BeautifulSoup para analisar o conteúdo HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encontrar todas as imagens na página
    all_images = soup.find_all('img')
    
    # Mostrar todos os URLs das imagens encontradas
    for img in all_images:
        if 'src' in img.attrs:
            print(img['src'])
    
    # Verificar se uma imagem de gato foi encontrada
    image_url = None
    for img in all_images:
        if 'src' in img.attrs and re.search(r'\.jpg$', img['src']):
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
else:
    print("Falha ao acessar o site. Código de status:", response.status_code)




#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')

mystring = f""" {data} AI Cat
#AI #GAN #thiscatdoesnotexist"""

#media = api.media_upload("cat_image.jpg")
#client.create_tweet(text=mystring, media_ids=[media.media_id]) 
