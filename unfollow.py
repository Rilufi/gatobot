import tweepy
from auth import api

 
followers = api.get_followers_ids(screen_name=api.me().screen_name)
#print("Followers", len(followers))
friends = api.get_friends_ids(screen_name=api.me().screen_name)
#print("You follow:", len(friends))
print("The difference between followers and following is:", len(friends)-len(followers))

for friend in friends:
    if friend not in followers:
        api.destroy_friendship(friend) 
