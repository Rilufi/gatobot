import tweepy
import os
import requests
import json
import random
import urllib.request
from datetime import datetime, timezone, timedelta
from auth import api, client
from PIL import Image
import google.generativeai as genai


# Inicializando api do Gemini
GOOGLE_API_KEY=os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro-vision')

def gemini_image(prompt, image_path):
    # Carregando a imagem
    imagem = Image.open(image_path)

    # Convertendo a imagem para o modo 'RGB' caso esteja em modo 'P'
    if imagem.mode == 'P':
        imagem = imagem.convert('RGB')

    # Gerando conteúdo com base na imagem e no prompt
    response = model.generate_content([prompt, imagem], stream=True)

    # Aguarda a conclusão da iteração antes de acessar os candidatos
    response.resolve()

    # Verificando a resposta
    if response.candidates and len(response.candidates) > 0:
        if response.candidates[0].content.parts and len(response.candidates[0].content.parts) > 0:
            return response.candidates[0].content.parts[0].text
        else:
            print("Nenhuma parte de conteúdo encontrada na resposta.")
    else:
        print("Nenhum candidato válido encontrado.")
    

# Functions for posting tweets
def post_tweet_with_replies(text, max_length=280):
    if len(text) <= max_length:
        # Post the tweet directly if it's within the character limit
        client.create_tweet(text=text)
    else:
        # Cut the text into chunks without splitting words
        chunks = get_chunks(text, max_length)
        # Post the first chunk
        response = client.create_tweet(text=next(chunks))
        # Save the ID of the first tweet
        reply_to_id = response.data['id']
        # Post subsequent chunks as replies to the first tweet
        for chunk in chunks:
            response = client.create_tweet(text=chunk, in_reply_to_tweet_id=reply_to_id)
            # Update the ID for the next reply
            reply_to_id = response.data['id']

# Function to split text into chunks without splitting words
def get_chunks(s, max_length):
    start = 0
    end = 0
    while start + max_length < len(s) and end != -1:
        end = s.rfind(" ", start, start + max_length + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]

# Function to get random cat image and resize it if needed
def get_random_cat():
    CAT_KEY = os.environ.get("CAT_KEY")
    url = "https://api.thecatapi.com/v1/images/search?format=json"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': CAT_KEY,
    }
    response = requests.get(url, headers=headers)
    todos = json.loads(response.text)
    site = todos[0].get('url')
    r = requests.get(site, allow_redirects=True)
    
    # Open the downloaded image
    with open('cat_image.jpg', 'wb') as f:
        f.write(r.content)
    
    # Open the image using Pillow
    img = Image.open('cat_image.jpg')

    # Check if image exceeds Twitter's size limit (5 MB)
    max_file_size = 5 * 1024 * 1024  # 5 MB in bytes
    if os.path.getsize('cat_image.jpg') > max_file_size:
        # Resize the image while maintaining aspect ratio
        img.thumbnail((1600, 1600))  # Resize the image to fit within 1600x1600 pixels

        # Save the resized image
        img.save('cat_image.jpg')

        print("Image resized to fit Twitter's size limit.")
    else:
        print("Image size is within Twitter's size limit.")

# Function to get random dog image
def get_random_dog():
    DOG_KEY = os.environ.get("DOG_KEY")
    url = "https://api.thedogapi.com/v1/images/search?format=json"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': DOG_KEY,
    }
    response = requests.get(url, headers=headers)
    todos = json.loads(response.text)
    site = todos[0].get('url')
    r = requests.get(site, allow_redirects=True)
    
    # Open the downloaded image
    with open('dog_image.jpg', 'wb') as f:
        f.write(r.content)
    
    # Open the image using Pillow
    img = Image.open('dog_image.jpg')

    # Check if image exceeds Twitter's size limit (5 MB)
    max_file_size = 5 * 1024 * 1024  # 5 MB in bytes
    if os.path.getsize('dog_image.jpg') > max_file_size:
        # Resize the image while maintaining aspect ratio
        img.thumbnail((1600, 1600))  # Resize the image to fit within 1600x1600 pixels

        # Save the resized image
        img.save('dog_image.jpg')

        print("Image resized to fit Twitter's size limit.")
    else:
        print("Image size is within Twitter's size limit.")

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
        filename = "fakecat.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded image: {filename}")
    else:
        print("Error downloading image.")

# Function to post AI-generated cat tweet
def post_ai_generated_cat_tweet():
    data = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
    response_gemini = gemini_image("Write a funny tweet rating this ai-generated cat image with twitter related hashtags","fakecat.jpg")
    if response_gemini == None:
        response_gemini = "#AI #GAN #thesecatsdonotexist"
    else:
        pass
    mystring = f""" {data} AI-generated Cat
{response_gemini}"""
    print(mystring)
    media = api.media_upload("fakecat.jpg")
    client.create_tweet(text=mystring, media_ids=[media.media_id])
    
# Function to post random cat tweet
def post_random_cat_tweet():
    data = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
    response_gemini = gemini_image("Write a funny and/or cute tweet about this cat image with twitter related hashtags",'cat_image.jpg')
    if response_gemini == None:
        response_gemini = "#CatsOfTwitter #cats #CatsOnTwitter"
    else:
        pass
    mystring = f""" {data} Surprise Cat
{response_gemini}"""
    print(mystring)
    media = api.media_upload("cat_image.jpg")
    response = client.create_tweet(text=mystring, media_ids=[media.media_id])
    cat_id = response.data['id']
    print(cat_id)
  #  recipient_id = '1737242580025212928'
  #  client.create_direct_message(participant_id = recipient_id, text = cat_id)
    api.create_favorite(cat_id)
    api.retweet(cat_id)

# Function to post random dog tweet
def post_random_dog_tweet():
    data = datetime.now().astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
    response_gemini = gemini_image("Write a funny and/or cute tweet about this dog image with twitter related hashtags",'dog_image.jpg')
    if response_gemini == None:
        response_gemini = "#DogsOfTwitter #dogs #DogsOnTwitter"
    else:
        pass
    mystring = f""" {data} Surprise Dog
{response_gemini}"""
    print(mystring)
    media = api.media_upload("dog_image.jpg")
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
    else:
        pass

def rate_status():
    # Get rate limit status
    response = api.rate_limit_status()

    # Check if the '/statuses/update' key exists in the response
    if '/statuses/update' not in response['resources']['statuses']:
        print("'/statuses/update' not found in rate limit status. Continuing script.")
    else:
        print("'/statuses/update' found in rate limit status. Exiting script.")
        exit()


# Main function
def main():
    # Checking rate limit before doing anything else
    rate_status()
    
    # Call necessary functions
    download_random_image()
    get_random_dog()
    get_random_cat()
    cat_fact = get_cat_fact()
    
    # Post tweets
    tweets = [post_tweet_with_replies(cat_fact), post_ai_generated_cat_tweet(), post_random_cat_tweet(), post_random_dog_tweet(), cattp()]
    for tweet in tweets:
        try:
            tweet
        except:
            pass

if __name__ == "__main__":
    main()
