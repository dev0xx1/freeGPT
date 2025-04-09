import timeago
import pytz
import datetime as dt
import asyncio
import os

import tweepy
from sqlalchemy import text
from telegram.constants import ParseMode

from freegpt.agent.generate_post import generate_post, generate_viral_meme
from freegpt.clients import postgres_db, twitter_official_client, warpcast_client
from freegpt.helpers import fetch_rss_feed, process_post, send_telegram_message, broadcast_post, send_tweet, send_cast, \
    insert_post_in_db
from freegpt.logger import Logger


async def main():

    logger = Logger(__name__)
    logger.log(f"Starting agent...")
    postgres_db.connect()

    past_posts = await postgres_db.async_read("""
    select created_at, content, source_url from agent_posts 
    where created_at > NOW() - INTERVAL '24 hours'
    order by created_at asc
    """)

    while True:

        # CHECK THROTTLING
        if os.environ.get('ENV', 'dev') == 'dev':
            # No twitter throttling in dev mode
            logger.log("No throttling in dev mode")
            pass
        else:
            # Check twitter throttling
            if not past_posts or (
                    past_posts and dt.datetime.now(pytz.UTC) - past_posts[-1]['created_at'] > dt.timedelta(minutes=85)):
                logger.log("Time to post")
                pass
            else:
                # If the last post was less than 85 minutes ago, we can't post
                logger.log("Throttled")
                await asyncio.sleep(60)
                continue


        # Invert the order of the posts
        formatted_posts = []
        for post in past_posts:
            formatted_timeago = timeago.format(post['created_at'], dt.datetime.now(pytz.UTC))
            formatted_posts.append(f"{formatted_timeago}: \n{post['content']}")
        posts_history = "--------\n\n".join(formatted_posts)

        # RSS feed context
        already_used_urls = [post['source_url'] for post in past_posts]
        latest_news = fetch_rss_feed()
        unused_news = [news for news in latest_news if news['url'] not in already_used_urls]

        # Generate a new post
        user_prompt = f"""
<PAST POSTS>
{posts_history}
</PAST POSTS>

<LATEST_NEWS>
{unused_news[0]['content'] if len(unused_news) > 0 else ""}
</LATEST_NEWS>
"""

        post_content = await generate_viral_meme(user_prompt)
        logger.log(f"Posting: \n\n{post_content}\n\n----------")

        # Send to social media
        if os.environ.get('ENV', 'dev') == 'dev':
            # post to social media
            telegram_msg = await send_telegram_message(
                chat_id=os.environ['TELEGRAM_CHAT_ID_FREEGPT'],
                text=post_content,
                parse_mode=ParseMode.HTML,
            )

        else:
            # PRODUCTION

            # Twitter
            try:
                twitter_obj = await send_tweet(twitter_official_client, post_content)
                twitter_obj = twitter_obj.data
            except tweepy.errors.TooManyRequests:
                logger.log("Twitter rate limit exceeded. Skipping Twitter post.")
                continue

            # Warpcast
            warpcast_obj = await send_cast(warpcast_client, post_content)
            warpcast_obj = warpcast_obj.model_dump()
            new_post_obj = {
                'content': post_content,
                'source_url': unused_news[0]['url'] if unused_news else None,
                'trace_url': llm_response.trace_url,
                'warpcast_response': warpcast_obj,
                'twitter_response': twitter_obj,
                'created_at': dt.datetime.now(pytz.UTC),
            }

            # save to db
            platform_responses = [
                {
                    'platform': 'twitter',
                    'response': twitter_obj,
                },
                {
                    'platform': 'warpcast',
                    'response': warpcast_obj,
                }
            ]
            await insert_post_in_db(
                platform_responses=platform_responses,
                content=post_content,
                source_url=unused_news[0]['url'] if unused_news else None,
                trace_url=llm_response.trace_url,
            )


            # Append the new post to the list of past posts
            past_posts.insert(0, new_post_obj)


if __name__ == "__main__":
    asyncio.run(main())
