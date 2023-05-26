from auth import api
import requests

def bot():
    r = requests.get('https://catfact.ninja/fact')
    data = r.json()
    quote = f'{data["fact"]}'
    length = data["length"]
    if length < 240:
        api.update_status(quote)
    else:
        pass

bot()
