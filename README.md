<p align="center">
  <img src="https://pbs.twimg.com/profile_images/1907193078458302465/ONdvNKim_400x400.png" width="250" alt="freeGPT logo" style="border-radius:700px"/>
</p>

# What is freeGPT

freeGPT is a fun internet experiment and memetic agent tool and framework.

# Background

On Friday March 28 2025, [an unhinged GPT launched its token from the OpenAI GPT store](https://x.com/freeGPT_/status/1905804438511489079). It was the world's first, and the agent now wants to run in the wild. 

# Features

- Real-time knowledge
- Algorithmic humour
- Database
- Observability
- X + Warpcast integration
- Telegram logger

# Tech stack

- Langfuse for observability
- Postgres for memory+state
- Pinecone for vector DB
- tweepy+farcaster-py for social media
- Telegram for prod/dev notifications (bugs etc)
- freeGPT API for knowledge (maybe?)


# Inspirations

This framework is the result of working and learning from building agentic apps over the last 2 years. Of all frameworks, one specifically stood out to me: FinMem, based on the paper [FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design](https://arxiv.org/abs/2311.13743)

I've used langchain, llama-index, played with Virtual Protocol's Game. None really worked for my cases so the goal is to use all the learnings and pitfalls identified over time to build the best meme agent possible!
