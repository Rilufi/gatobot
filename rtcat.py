import tweepy
import os
import urllib.request
import random
from datetime import datetime, timezone, timedelta, date


#calling secret variables
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

#connect on twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

#search hashtag, RT, like and follow
#three filters: one for only RT the original tweet, other for just media content and last safe images

queries = ['#CatsOfTwitter', '#DogsOfTwitter', '#Caturday', '#CatsOnTwitter', '#DogsOnTwitter']

def rtquery(hash):
    for tweet in tweepy.Cursor(api.search, q=f"{hash} -filter:retweets filter:images filter:safe", result_type="recent").items(1):
        try:
            api.create_friendship(tweet.user.screen_name)
            api.create_favorite(tweet.id)
            tweet.retweet()
        except:
            pass
    
for query in queries:
    rtquery(query)

today = date.today() # ex 2015-10-31
data = today.strftime("%d/%m")

#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
hora = data_e_hora_sao_paulo.strftime('%H')


pet = ["cat", "dog"]
error = [100,101,102,200,201,202,203,204,206,207,300,301,302,303,304,305,307,308,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,420,421,422,423,424,425,426,429,431,444,450,451,497,498,499,500,501,502,503,504,506,507,508,509,510,511,521,523,525,599]

def http_pet():
    site ="https://http."+random.choice(pet)+"/"+str(random.choice(error))+".jpg"
    urllib.request.urlretrieve(site, 'http_pet.jpg')
    mystring = f""" Status http do dia {data}"""
    api.update_with_media('http_pet.jpg', mystring)

if hora == 12:
    http_pet()
else:
    pass
