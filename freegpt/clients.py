import os
from farcaster import Warpcast
from langfuse import Langfuse
import tweepy
from telegram import Bot

from freegpt.db.postgres_db import PostgresDB

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

postgres_db = PostgresDB(
    username=os.environ["POSTGRES_USERNAME"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    db_name=os.environ["POSTGRES_DB"],
)

freegpt_telegram_bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN_FREEGPT'])

if 'FARCASTER_MNEMONIC' in os.environ:
    os.environ['FARCASTER_MNEMONIC'] = os.environ['FARCASTER_MNEMONIC'].replace('"', '').replace("'", "")
    warpcast_client = Warpcast(mnemonic=os.environ['FARCASTER_MNEMONIC'])
    warpcast_client.get_healthcheck()
else:
    warpcast_client = None