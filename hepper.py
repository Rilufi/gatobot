from auth import api
import requests

def bot():
    r = requests.get('https://catfact.ninja/fact')
    data = r.json()
    quote = f'{data["fact"]}'
    length = data["length"]
    if length < 240:
        api.create_tweet(text = quote)
    else:
        pass

bot()
