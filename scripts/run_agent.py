import timeago
import pytz
import datetime as dt
import asyncio
import os

import tweepy
from farcaster.models import Parent
from telegram.constants import ParseMode

from freegpt.agent.generate_post import generate_post
from freegpt.clients import postgres_db, twitter_official_client, warpcast_client
from freegpt.helpers import fetch_rss_feed, send_telegram_message, send_tweet, send_cast, \
    insert_post_in_db
from freegpt.logger import Logger


async def main():

    logger = Logger(__name__)
    logger.log(f"Starting agent...")
    postgres_db.connect()

    while True:

        if int(os.environ.get('IS_ON', 0)) == 0:
            logger.log("Agent is OFF, Sleeping...")
            await asyncio.sleep(60 * 5)
            continue

        recent_post = await postgres_db.async_read("""
            SELECT EXISTS (
                SELECT 1
                FROM agent_posts
                WHERE created_at > now() - INTERVAL '85 minutes'
            ) AS is_recent
        """)

        if recent_post and recent_post[0]['is_recent']:
            logger.log("Waiting for 5 minutes...")
            await asyncio.sleep(60 * 5)
            continue


        # Fetch memory
        logger.log("Fetching past posts...")
        past_posts = await postgres_db.async_read("""
        select created_at, content, source_url from agent_posts 
        where created_at > NOW() - INTERVAL '24 hours'
        order by created_at asc
        """)

        formatted_posts = []
        for post in past_posts:
            formatted_timeago = timeago.format(post['created_at'], dt.datetime.now(pytz.UTC))
            formatted_posts.append(f"{formatted_timeago}: \n{post['content']}")
        posts_history = "--------\n\n".join(formatted_posts)

        # RSS feed context
        already_used_urls = [post['source_url'] for post in past_posts]
        latest_news = fetch_rss_feed()
        unused_news = [news for news in latest_news if news['url'] not in already_used_urls]
        if len(unused_news) == 0:
            logger.log("No new news, sleeping...")
            await asyncio.sleep(60 * 5)
            continue


        # Generate a new post
        latest_news_article_content = unused_news[0]['content']
        latest_news_article_url = unused_news[0]['url']
        meme_context = f"""
<PAST POSTS>
{posts_history}
</PAST POSTS>

<LATEST_NEWS>
{latest_news_article_content}
</LATEST_NEWS>
"""

        post_content, trace_url = await generate_post(context=meme_context,
                                                      model='gemini/gemini-1.5-pro')

        channels = os.environ['SOCIAL_CHANNELS']
        channels = [channel.strip() for channel in channels.split(',')]

        platform_responses = []

        if 'x' in channels:
            logger.log("Posting to X...")
            try:
                twitter_obj = await send_tweet(twitter_official_client, post_content+f"\n\n{latest_news_article_url}")
                twitter_obj = twitter_obj.data
                platform_responses.append({
                    'platform': 'twitter',
                    'response': twitter_obj,
                })
            except tweepy.errors.TooManyRequests:
                logger.log("Twitter rate limit exceeded, skipping...")
                pass

        if 'farcaster' in channels:
            logger.log("Posting to Farcaster...")

            warpcast_obj = await send_cast(warpcast_client, post_content)
            parent_r = Parent(
                fid=int(os.environ['FID']),
                hash=warpcast_obj.cast.hash
            )
            warpcast_client.post_cast(text='source: ', parent=parent_r, embeds=[latest_news_article_url])
            platform_responses.append({
                'platform': 'warpcast',
                'response': warpcast_obj.model_dump(),
            })

        if 'telegram' in channels:
            logger.log("Posting to Telegram...")
            telegram_msg = await send_telegram_message(
                chat_id=os.environ['TELEGRAM_CHAT_ID_FREEGPT'],
                text=post_content,
                parse_mode=ParseMode.HTML,
            )
            platform_responses.append({
                'platform': 'telegram',
                'response': telegram_msg,
            })

        if 'console' in channels:
            print(f"\n\n{post_content}\n\n----------")
            platform_responses.append({
                'platform': 'console',
                'response': post_content,
            })

        # save to db
        if platform_responses:
            await insert_post_in_db(
                platform_responses=platform_responses,
                content=post_content,
                source_url=unused_news[0]['url'] if unused_news else None,
                trace_url=trace_url,
            )



if __name__ == "__main__":
    asyncio.run(main())
