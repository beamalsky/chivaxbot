import time
import sys
import tweepy
import sentry_sdk

from chivaxbot import get_tweet
from chivaxbot_gif import get_gif_tweet
from utils import get_bucket, upload_to_gcloud

LOCAL_DEVELOPMENT = True

if LOCAL_DEVELOPMENT:
    from secrets import *

else:
    from os import environ

    API_KEY = environ['API_KEY']
    API_KEY_SECRET = environ['API_KEY_SECRET']
    ACCESS_TOKEN = environ['ACCESS_TOKEN']
    ACCESS_TOKEN_SECRET = environ['ACCESS_TOKEN_SECRET']
    SENTRY_URL = environ['SENTRY_URL']
    GOOGLE_APPLICATION_CREDENTIALS = environ['GOOGLE_APPLICATION_CREDENTIALS']
    sentry_sdk.init(
        SENTRY_URL,
        traces_sample_rate=1.0
    )

tweet = get_tweet()
tweet2 = get_gif_tweet()

if not LOCAL_DEVELOPMENT:
    # upload tweet images and text to Twitter
    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # first tweet
    images = [tweet["deaths_map_path"], tweet["vax_map_path"]]
    alt_text = tweet["alt_text"]
    media_ids = [api.media_upload(i).media_id_string for i in images]
    for id in media_ids:
        api.create_media_metadata(
            media_id=id,
            alt_text=alt_text
        )

    original_tweet = api.update_status(
        status=tweet["tweet_text"] + "\n\nWho is dying:		   Who is vaccinated:",
        media_ids=media_ids
    )

    # second tweet
    gif_id = api.media_upload(tweet2["gif_path"]).media_id_string
    api.create_media_metadata(
        media_id=gif_id,
        alt_text=tweet2["alt_text"]
    )
    api.update_status(
        in_reply_to_status_id=original_tweet.id,
        status=tweet["tweet_text"] + "\n\n" + tweet2["tweet_text"],
        media_ids=[gif_id],
    )

    # upload latest files to Google Cloud for embeds
    bucket = get_bucket("chivaxbot", GOOGLE_APPLICATION_CREDENTIALS)
    gcloud_uploads = ["deaths_map_path_latest", "vax_map_path_latest", "sentence_path_latest"]

    for path in gcloud_uploads:
        upload_to_gcloud(
            bucket,
            tweet[path]
        )