import os
import json
import requests
import tweepy
from datetime import datetime, timezone, timedelta
from auth import api, client

#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data = data_e_hora_sao_paulo.strftime('%H:%M')

mystring = f""" {data} Surprise Dog
#DogsOfTwitter #dogs #DogsOnTwitter"""

def get_random_dog(filename: str='temp') -> None:

    r = requests.get('https://dog.ceo/api/breeds/image/random')
    rd = json.loads(r.content)
    r2 = requests.get(rd['message'])

    with open(filename, 'wb') as image:
        for chunk in r2:
            image.write(chunk)


def main(message: str, filename: str='temp') -> None:
    get_random_dog(filename) 

    try:
        media = api.media_upload(filename)
        client.create_tweet(text=message, media_ids=[media.media_id])
        #api.update_with_media(filename, status=message)
        print('Tweet successfully sent!')


    except Exception as e:
        print('Error sending tweet \n %s' % e)


if __name__ == '__main__':

    main(mystring)
