import tweepy
import sentry_sdk

from chivaxbot import get_tweet
from chivaxbot_gif import get_gif_tweet
from utils import get_bucket, upload_to_gcloud

LOCAL_DEVELOPMENT = False

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

tweet1_dict = get_tweet()
tweet2_dict = get_gif_tweet()

if not LOCAL_DEVELOPMENT:
    # upload tweet images and text to Twitter
    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # first tweet
    images = [tweet1_dict["deaths_map_path"], tweet1_dict["vax_map_path"]]
    alt_text = tweet1_dict["alt_text"]
    media_ids = [api.media_upload(i).media_id_string for i in images]
    for id in media_ids:
        api.create_media_metadata(
            media_id=id,
            alt_text=alt_text
        )

    tweet1 = api.update_status(
        status=tweet1_dict["tweet_text"] + "\n\nWho is dying:		   Who is vaccinated:",
        media_ids=media_ids
    )

    # second tweet
    gif_id = api.media_upload(tweet2_dict["gif_path"]).media_id_string
    api.create_media_metadata(
        media_id=gif_id,
        alt_text=tweet2_dict["alt_text"]
    )
    tweet2 = api.update_status(
        in_reply_to_status_id=tweet1.id,
        status=tweet1_dict["tweet_text"],
        media_ids=[gif_id],
    )

    # third tweet
    tweet3_status = '''
        Read the latest on Chicago's widening vaccine disparity from @maerunes for @SouthSideWeekly: https://southsideweekly.com/chicagos-vaccine-disparity-widens/
    '''
    tweet3 = api.update_status(
        in_reply_to_status_id=tweet2.id,
        status=tweet3_status,
    )
    # upload latest files to Google Cloud for embeds
    bucket = get_bucket("chivaxbot", GOOGLE_APPLICATION_CREDENTIALS)
    gcloud_uploads = ["deaths_map_path_latest", "vax_map_path_latest", "sentence_path_latest"]

    for path in gcloud_uploads:
        upload_to_gcloud(
            bucket,
            tweet1_dict[path]
        )