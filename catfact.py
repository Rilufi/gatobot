import requests
from auth import client

def get_chunks(s, maxlength):
    start = 0
    end = 0
    while start + maxlength < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]

def post_tweet_with_replies(text, max_length=280):
    if len(text) <= max_length:
        # Post the tweet directly if it's within the character limit
        client.create_tweet(text=text)
    else:
        # Cut the text into chunks
        chunks = list(get_chunks(text, max_length))
        # Post the first chunk
        response = client.create_tweet(text=chunks[0])
        # Save the ID of the first tweet
        reply_to_id = response.data['id']
        # Post subsequent chunks as replies to the first tweet
        for chunk in chunks[1:]:
            response = client.create_tweet(text=chunk, in_reply_to_tweet_id=reply_to_id)
            # Update the ID for the next reply
            reply_to_id = response.data['id']

def bot():
    r = requests.get('https://catfact.ninja/fact')
    data = r.json()
    fact = data["fact"]
    length = data["length"]
    if "skins" in fact:
        pass  # Skip facts containing "skins"
    elif length <= 280:
        # Post the fact directly
        post_tweet_with_replies(fact)
    else:
        # Post the fact in chunks as replies
        post_tweet_with_replies(fact)

bot()
