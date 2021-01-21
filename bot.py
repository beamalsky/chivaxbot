import time
import sys
import tweepy

from chivaxbot import get_tweet

LOCAL_DEVELOPMENT = False

if LOCAL_DEVELOPMENT:
    from secrets import *

else:
    from os import environ

    API_KEY = environ['API_KEY']
    API_KEY_SECRET = environ['API_KEY_SECRET']
    ACCESS_TOKEN = environ['ACCESS_TOKEN']
    ACCESS_TOKEN_SECRET = environ['ACCESS_TOKEN_SECRET']

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
tweet = get_tweet()

images = [tweet["deaths_map_path"], tweet["vax_map_path"]]
media_ids = [api.media_upload(i).media_id_string for i in images]
api.update_status(
    status=tweet["tweet_text"], 
    media_ids=media_ids
)
