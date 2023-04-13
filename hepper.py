from auth import api
import random

lines=open('products.txt').read().splitlines()
status = random.choice(lines)
mystring = f""" Looking for the perfect way to spoil your furry friend? Look no further than Hepper! High-quality pet products are designed with both you and your pet in mind.
#PetLovers #CatsOfTwitter #PetProducts
{status}"""

try:
    api.update_status(mystring)
except:
    pass
