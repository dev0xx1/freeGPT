from langfuse import Langfuse
import tweepy
import os

langfuse_client = Langfuse(
    public_key=os.environ['LANGFUSE_PUBLIC_KEY'],
    secret_key=os.environ['LANGFUSE_SECRET_KEY'],
    host=os.environ['LANGFUSE_HOST'],
    flush_interval=0.1,
)

twitter_official_client = tweepy.Client(
    consumer_key=os.environ['TWITTER_CONSUMER_API_KEY'],
    consumer_secret=os.environ['TWITTER_CONSUMER_API_SECRET'],
    access_token=os.environ['TWITTER_ACCESS_TOKEN'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
)

