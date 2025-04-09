import asyncio
import re
import feedparser
import tweepy
from bs4 import BeautifulSoup
from telegram.constants import ParseMode
from tenacity import stop_after_attempt, wait_fixed, retry, wait_exponential, retry_if_exception, \
    retry_if_exception_type
import json
import os
import socket
from datetime import datetime
from sqlalchemy import create_engine, text, select
from sqlalchemy.exc import OperationalError, TimeoutError, DisconnectionError, DatabaseError, DBAPIError
from psycopg2 import OperationalError as Psycopg2OperationalError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
# get machine user name
import getpass

from freegpt.clients import postgres_db


username = getpass.getuser()
DB_RETRIES = int(os.environ.get('DB_RETRIES', 0))
WAIT_SEC = int(os.environ.get('WAIT_SEC', 0))

RETRIES = 0 if 'dev0xx' == username else 10
exceptions = (socket.gaierror, OperationalError, TimeoutError, DisconnectionError, DatabaseError, DBAPIError,
              Psycopg2OperationalError)


def fetch_rss_feed():
    feed_url = "http://feeds.feedburner.com/zerohedge/feed"
    feed = feedparser.parse(feed_url)
    objects = []
    for entry in feed.entries:
        title = entry.title
        url = entry.link
        timestamp = entry.published
        soup = BeautifulSoup(entry.summary, 'html.parser')
        clean_text = soup.get_text(separator='\n', strip=True)
        parsed_timestamp = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %z')

        objects.append({
            'title': title,
            'url': url,
            'timestamp': parsed_timestamp,
            'content': clean_text
        })

    return objects


def remove_emojis(text):
    # This pattern covers most modern emoji Unicode ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', text)


def process_post(content):
    content = content.replace("🚀", "")
    # Remove all links
    content = re.sub(r'http\S+', '', content)
    # remove hashtags
    content = re.sub(r'#\w+', '', content)
    # Remove Join CTA
    cleaned_text = re.sub(r'\bJoin the[^\n.?!]*[.?!]?\s*', '', content)
    # Remove emojis
    cleaned_text = remove_emojis(cleaned_text)

    cleaned_text = cleaned_text.strip()
    return cleaned_text


@retry(
    reraise=True,
    stop=stop_after_attempt(RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
async def send_telegram_message(telegram_bot, chat_id, message):
    return await telegram_bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode=ParseMode.HTML
    )


def is_retryable_exception(exception):
    # Return False if it's a TooManyRequests exception, True otherwise
    return not isinstance(exception, tweepy.errors.TooManyRequests)


@retry(
    reraise=True,
    stop=stop_after_attempt(RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception(is_retryable_exception),
)
async def send_tweet(twitter_client, message):
    return twitter_client.create_tweet(
        text=message,
    )


@retry(
    reraise=True,
    stop=stop_after_attempt(RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
async def send_cast(warpcast_client, content):
    # Send a cast
    response = warpcast_client.post_cast(content)
    return response


async def broadcast_post(
        content,
        twitter_client=None,
        warpcast_client=None,
        telegram_bot=None,
        telegram_chat_id=None,
):
    # Create async tasks for each social media platform if clients are provided
    tasks = []
    client_names = []
    if twitter_client:
        tasks.append(send_tweet(twitter_client, content))
        client_names.append('twitter')
    if warpcast_client:
        tasks.append(send_cast(warpcast_client, content))
        client_names.append('warpcast')
    if telegram_bot:
        tasks.append(send_telegram_message(telegram_bot, telegram_chat_id, content))
        client_names.append('telegram')

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)

    # Return the results of the tasks in a dictionary with the client name as the key
    return {client: result for client, result in zip(client_names, results)}


@retry(
    reraise=True,
    stop=stop_after_attempt(DB_RETRIES),
    wait=wait_fixed(WAIT_SEC),
    retry=retry_if_exception_type(exceptions)
)
async def insert_post_in_db(content,
                            source_url,
                            trace_url,
                            platform_responses=[]):
    async with postgres_db.async_session_scope() as session:
        result = await session.execute(
            text("""
            INSERT INTO agent_posts (content, source_url, trace_url)
            VALUES (:content, :source_url, :trace_url)
            RETURNING id;
            """),
            {"content": content,
             "source_url": source_url,
             "trace_url": trace_url}
        )
        agent_post_id = result.scalar_one()

        # Step 2: Insert each platform response
        for response in platform_responses:
            await session.execute(
                text("""
                INSERT INTO social_media_posts (agent_post_id, response, platform)
                VALUES (:agent_post_id, :response, :platform);
                """),
                {
                    "agent_post_id": agent_post_id,
                    "platform": response["platform"],
                    "response": json.dumps(response['response']),
                }
            )
