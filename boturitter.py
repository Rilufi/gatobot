import tweepy
import os
import requests
import json
import random
from datetime import datetime, timezone, timedelta
from auth import api, client

# Functions for posting tweets
def post_tweet_with_replies(text, max_length=280):
    if len(text) <= max_length:
        # Post the tweet directly if it's within the character limit
        client.create_tweet(text=text)
    else:
        # Cut the text into chunks
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        # Post the first chunk
        response = client.create_tweet(text=chunks[0])
        # Save the ID of the first tweet
        reply_to_id = response.data['id']
        # Post subsequent chunks as replies to the first tweet
        for chunk in chunks[1:]:
            response = client.create_tweet(text=chunk, in_reply_to_tweet_id=reply_to_id)
            # Update the ID for the next reply
            reply_to_id = response.data['id']

# Function to get random cat image
def get_random_cat():
    CAT_KEY = os.environ.get("CAT_KEY")
    url = "https://api.thecatapi.com/v1/images/search?format=json"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': CAT_KEY,
        "width": 1600,
        "height": 900,
    }
    response = requests.get(url, headers=headers)
    todos = json.loads(response.text)
    site = todos[0].get('url')
    r = requests.get(site, allow_redirects=True)
    open('cat_image.jpg', 'wb').write(r.content)

# Function to get random dog image
def get_random_dog(filename='temp'):
    r = requests.get('https://dog.ceo/api/breeds/image/random')
    rd = json.loads(r.content)
    r2 = requests.get(rd['message'])

    with open(filename, 'wb') as image:
        for chunk in r2:
            image.write(chunk)

# Function to download a random image
def download_random_image():
    # Generate random numbers for image URL
    w = random.randint(1, 6)
    x = random.randint(1, 9)
    y = random.randint(0, 9)
    z = random.randint(0, 9)

    # Construct image URL
    image_url = f"https://d2ph5fj80uercy.cloudfront.net/0{w}/cat{x}{y}{z}.jpg"

    # Make HTTP request to download image
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the image locally
        filename = "cat_image.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded image: {filename}")
    else:
        print("Error downloading image.")

# Function to post AI-generated cat tweet
def post_ai_generated_cat_tweet():
    data = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
    mystring = f""" {data} AI-generated Cat
    #AI #GAN #thesecatsdonotexist"""
    media = api.media_upload("cat_image.jpg")
    client.create_tweet(text=mystring, media_ids=[media.media_id])

# Function to post random cat tweet
def post_random_cat_tweet():
    data = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
    mystring = f""" {data} Surprise Cat
    #CatsOfTwitter #cats #CatsOnTwitter"""
    media = api.media_upload("cat_image.jpg")
    client.create_tweet(text=mystring, media_ids=[media.media_id])

# Function to get a cat fact from catfact.ninja
def get_cat_fact():
    # Loop until a fact without the word "skins" is obtained
    while True:
        r = requests.get('https://catfact.ninja/fact')
        data = r.json()
        fact = data["fact"]
        length = data["length"]
        if "skins" not in fact:
            return fact

# Function to post random dog tweet if the hour is 12
def cattp():
    # Get current hour
    hora = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H')

    if hora == '12':
        #list of errors and cat or dog
        pet = ["cat", "dog"]
        error = [100,101,102,200,201,202,203,204,206,207,300,301,302,303,304,305,307,308,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,420,421,422,423,424,425,426,429,431,444,450,451,497,498,499,500,501,502,503,504,506,507,508,509,510,511,521,523,525,599]

        # Get random image from one of these sites and post
        site ="https://http."+random.choice(pet)+"/"+str(random.choice(error))+".jpg"
        urllib.request.urlretrieve(site, 'http_pet.jpg')
        mystring = f""" HTTP status of the day {datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%d/%m')}"""
        media = api.media_upload("http_pet.jpg")
        client.create_tweet(text=mystring, media_ids=[media.media_id])

# Main function
def main():
    # Call necessary functions
    download_random_image()
    get_random_dog()
    get_random_cat()
    cat_fact = get_cat_fact()

    # Post tweets
    post_tweet_with_replies(cat_fact)
    post_ai_generated_cat_tweet()
    post_random_cat_tweet()
    cattp()

if __name__ == "__main__":
    main()
