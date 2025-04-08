import timeago
import pytz
import datetime as dt
import asyncio
import os

from langfuse.decorators import observe
from telegram.constants import ParseMode

from freegpt.agent.generate_post import generate_post
from freegpt.clients import postgres_db, freegpt_telegram_bot, twitter_official_client, warpcast_client
from freegpt.helpers import fetch_rss_feed, process_post, send_tweet, send_telegram_message, send_cast
from freegpt.logger import Logger

#TODO - Prompt engineering to avoid repeating itself
#TODO - Fix 280 characters limit
#TODO - Remove mentions of crypto
#TODO - Add network channel columns to DDL
#TODO - Implement broadcasting and msg response saving


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
            if not past_posts or (past_posts and dt.datetime.now(pytz.UTC) - past_posts[0]['created_at'] > dt.timedelta(minutes=15)):
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

        llm_response = await generate_post(user_prompt)
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
            logger.log(f"Posting to X : \n\n{post_content}\n\n----------")

            # Send to Twitter/X
            tweet = await send_tweet(
                twitter_client=twitter_official_client,
                message=post_content,
            )

            # Send to Warpcast
            #cast = await send_cast(
            #    warpcast_client=warpcast_client,
            #    content=post_content,
            #)

            # Share on Telegram to start a Raid


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
