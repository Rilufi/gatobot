import tweepy
from auth import api

 
followers = api.followers_ids(screen_name=api.me().screen_name)
print("Followers", len(followers))
friends = api.friends_ids(screen_name=api.me().screen_name)
print("You follow:", len(friends))
print("The difference between followers and following is:", len(friends)-len(followers))

for friend in friends:
    if friend not in followers:
        api.destroy_friendship(friend) 
print("Now you're following:", len(friends))
