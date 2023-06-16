import tweepy
import os
import urllib.request
import random
from datetime import date, timezone, timedelta, datetime
from auth import api, client

#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
hora = data_e_hora_sao_paulo.strftime('%H')

#what day is it?
today = date.today() # ex 2015-10-31
data = today.strftime("%d/%m")

#search last entry on specific account, RT and like
#three filters: one for only RT the original tweet, other for just media content and last safe images
queries = ['hamstersmp4', 'CreatureTikToks', 'CatWorkers', 'weirdlilguys', 'PetWorld02', 'genius_dogs', 'gatinarios', 'Thereisnocat_', 'TranslatedCats', 'TweetsOfCats', 'nywolforg', 'hourlywolvesbot', 'HutCat', 'DogsTwt', 'twtCats', 'Bodegacats']

def rtquery(hash):
#    for tweet in tweepy.Cursor(api.search, q=f"from:{hash} -filter:retweets -filter:replies filter:media filter:safe").items(1):
    tweet = api.search_recent_tweets(f"{hash} -filter:retweets -filter:replies filter:media filter:safe")
    api.like(tweet.id)
    tweet.retweet()

#for query in queries:
#    rtquery(query)

#list of errors and cat or dog
pet = ["cat", "dog"]
error = [100,101,102,200,201,202,203,204,206,207,300,301,302,303,304,305,307,308,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,420,421,422,423,424,425,426,429,431,444,450,451,497,498,499,500,501,502,503,504,506,507,508,509,510,511,521,523,525,599]

#get random image from one of this sites and post
def http_pet():
    site ="https://http."+random.choice(pet)+"/"+str(random.choice(error))+".jpg"
    urllib.request.urlretrieve(site, 'http_pet.jpg')
    mystring = f""" HTTP status of the day {data}"""
#    api.update_with_media('http_pet.jpg', mystring)
    media = api.media_upload("http_pet.jpg")
    client.create_tweet(text=mystring, media_ids=[media.media_id])
    
def hepper():
    lines=open('products.txt').read().splitlines()
    status = random.choice(lines)
    mystring = f""" Looking for the perfect way to spoil your furry friend? Look no further than Hepper! High-quality pet products are designed with both you and your pet in mind.
#PetLovers #CatsOfTwitter #PetProducts
    {status}"""

    try:
        client.create_tweet(text = mystring)
    except:
        pass

if hora == '12':
#    rtquery('nasobot')
    http_pet()
#    unfollower()
else:
    hepper()
