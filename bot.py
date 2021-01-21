import time
import sys
import tweepy
from pprint import pprint

from chivaxbot import get_tweet

LOCAL_DEVELOPMENT = True

if LOCAL_DEVELOPMENT:
    from secrets import *

else:
    from os import environ

    CONSUMER_KEY = environ['CONSUMER_KEY']
    CONSUMER_SECRET = environ['CONSUMER_SECRET']
    ACCESS_KEY = environ['ACCESS_KEY']
    ACCESS_SECRET = environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

tweet = get_tweet()

images = [tweet["deaths_map_path"], tweet["vax_map_path"]]
media_ids = [api.media_upload(i).media_id_string for i in images]
api.update_status(
    status=tweet["tweet_text"], 
    media_ids=media_ids
)
