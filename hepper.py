from auth import api
import random
import requests
from datetime import date, timezone, timedelta, datetime

#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
hora = data_e_hora_sao_paulo.strftime('%H')

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

def hepper():
    lines=open('products.txt').read().splitlines()
    status = random.choice(lines)
    mystring = f""" Looking for the perfect way to spoil your furry friend? Look no further than Hepper! High-quality pet products are designed with both you and your pet in mind.
    #PetLovers #CatsOfTwitter #PetProducts
    {status}"""

    try:
        api.update_status(mystring)
    except:
        pass

   if hora == '12':
        hepper()
   else: 
        pass
