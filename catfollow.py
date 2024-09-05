import os
import requests
from atproto import Client


# Inicializando o cliente do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky

client = Client(base_url='https://bsky.social')
client.login(BSKY_HANDLE, BSKY_PASSWORD)

data = client.app.bsky.feed.get_feed_generator({
    'feed': 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot'
})

view = data.view
creator = view.creator
display_name = view.display_name
avatar = view.avatar
like_count = view.like_count

print(view,creator,display_name,avatar,like_count)
