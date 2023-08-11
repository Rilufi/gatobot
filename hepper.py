from auth import api, client
import requests

def bot():
    r = requests.get('https://catfact.ninja/fact')
    data = r.json()
    quote = f'{data["fact"]}'
    length = data["length"]
    if "skins" in quote:
        pass
    elif length < 240:
        client.create_tweet(text = quote)
    else:
        pass

bot()
