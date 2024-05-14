import tweepy
from datetime import datetime, timezone, timedelta
import os
import requests
import random
from auth import api, client


def download_random_image():
    # Gerar valores aleatórios para w, x, y, z
    w = random.randint(1, 6)
    x = random.randint(1, 9)
    y = random.randint(0, 9)
    z = random.randint(0, 9)

    # Construir a URL da imagem
    image_url = f"https://d2ph5fj80uercy.cloudfront.net/0{w}/cat{x}{y}{z}.jpg"

    # Fazer o pedido HTTP para baixar a imagem
    response = requests.get(image_url)

    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Salvar a imagem na pasta local
        #filename = f"cat_{w}{x}{y}{z}.jpg"
        filename = "cat_image.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f"Imagem baixada: {filename}")
    else:
        print("Erro ao baixar a imagem.")

if __name__ == "__main__":
    download_random_image()

#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')

mystring = f""" {data} AI-generated Cat
#AI #GAN #thesecatsdonotexist"""

media = api.media_upload("cat_image.jpg")
client.create_tweet(text=mystring, media_ids=[media.media_id]) 
