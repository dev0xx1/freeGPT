import timeago
import pytz
import datetime as dt
import asyncio
import os

from langfuse.decorators import observe
from telegram.constants import ParseMode

from freegpt.agent.generate_post import generate_post
from freegpt.clients import postgres_db, freegpt_telegram_bot, twitter_official_client
from freegpt.helpers import fetch_rss_feed, process_post, send_tweet, send_telegram_message
from freegpt.logger import Logger


@observe(as_type='span', name='freegpt_agent')
async def main():

    logger = Logger(__name__)
    logger.log(f"Starting agent...")
    postgres_db.connect()

    past_posts = await postgres_db.async_read("""
    select created_at, content, source_url from agent_posts 
    where created_at > NOW() - INTERVAL '24 hours'
    order by created_at desc
    """)

    while True:

        # UPDATE CONTEXT
        # Post history

        if os.environ.get('ENV', 'dev') == 'dev':
            # No twitter throttling in dev mode
            pass
        else:

            # Check twitter throttling
            if dt.datetime.now(pytz.UTC) - past_posts[0]['created_at'] > dt.timedelta(minutes=85):
                logger.log("Ok to post")
                pass
            else:
                # If the last post was less than 85 minutes ago, we can't post
                logger.log("Throttled")
                await asyncio.sleep(60)
                continue

        # Invert the order of the posts
        past_posts = past_posts[::-1]
        formatted_posts = []
        for post in past_posts:
            post['created_at'] = timeago.format(post['created_at'], dt.datetime.now(pytz.UTC))
            formatted_posts.append(f"{post['created_at']}: {post['content']}")
        posts_context = "--------\n\n".join(formatted_posts)

        # RSS feed context
        already_used_urls = [post['source_url'] for post in past_posts]
        latest_news = fetch_rss_feed()
        unused_news = [news for news in latest_news if news['url'] not in already_used_urls]

        rss_feed_context = ""
        if unused_news:
            rss_feed_context = f"""
<LATEST_NEWS>
{unused_news[0]['content']}
</LATEST_NEWS>
"""

        context = f"{posts_context}------\n\n{rss_feed_context}"

        # Generate a new post
        llm_response = await generate_post(context)
        post_content = llm_response.processed.split('<post>')[1].split('</post>')[0].strip()

        post_content = process_post(post_content)

        if os.environ.get('ENV', 'dev') == 'dev':
            # post to social media
            telegram_msg = await send_telegram_message(
                chat_id=os.environ['TELEGRAM_CHAT_ID_FREEGPT'],
                text=post_content,
                parse_mode=ParseMode.HTML,
            )
            raw_obj = telegram_msg.to_dict()
        else:
            # post to social media
            tweet = send_tweet(
                twitter_client=twitter_official_client,
                message=post_content,
            )

            await send_telegram_message(
                telegram_bot=freegpt_telegram_bot,
                chat_id=os.environ['TELEGRAM_CHAT_ID_FREEGPT'],
                message=f"https://x.com/freeGPT_/status/{tweet.data['id']}",
            )
            raw_obj = tweet.data

        # save to db

        new_post_obj = {
            'content': post_content,
            'channel_object_raw': raw_obj,
            'source_url': unused_news[0]['url'] if unused_news else None,
            'trace_url':llm_response.trace_url,
        }

        await postgres_db.async_insert(
            table_name='agent_posts',
            rows=[
                new_post_obj
            ]
        )

        # Append the new post to the list of past posts
        new_post_obj['created_at'] = dt.datetime.now(pytz.UTC)
        past_posts.insert(0, new_post_obj)



if __name__ == "__main__":
    asyncio.run(main())
