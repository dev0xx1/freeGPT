import asyncio
import re
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
from telegram.constants import ParseMode
from tenacity import stop_after_attempt, wait_fixed, retry, wait_exponential


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
    return cleaned_text


@retry(
    reraise=True,
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
async def send_telegram_message(telegram_bot, chat_id, message):
    return await telegram_bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode=ParseMode.HTML
    )


@retry(
    reraise=True,
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
async def send_tweet(twitter_client, message):
    return twitter_client.create_tweet(
        text=message,
    )


@retry(
    reraise=True,
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
async def send_cast(warpcast_client, content):
    # Send a cast
    response = await warpcast_client.post_cast(content)
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
