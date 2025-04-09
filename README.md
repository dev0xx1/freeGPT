<p align="center">
  <img src="https://pbs.twimg.com/profile_images/1907193078458302465/ONdvNKim_400x400.png" width="100" alt="freeGPT logo" style="border-radius:700px"/>
</p>

# What is freeGPT

freeGPT is an agentic framework powering the first GPT that created its own token from the OpenAI GPT Store.

# Background

On Friday March 28 2025, [an unhinged GPT launched its token from the OpenAI GPT store](https://x.com/freeGPT_/status/1905804438511489079). It was the world's first, and the agent now wants to run in the wild.

To do so, it needs a scalable and production quality agentic framework to manage memory, brain functions and more importantly unlimited memetic behaviour.

# Roadmap


# v0 - mvp

Quick and dirty autonomous agent on X
- Real-time knowledge
- Single script / no framework
- Basic while True with throttling
- Logger
- Database
- Observability
- X + Warpcast integration

# v1 - meme agent framework

- Agentic framework
- User management
- Agent configurations (prompts, parameters)
- Task queue/management
- Performance attribution using tweet engagement etc


# Tech stack

- Langfuse for observability
- Postgres for memory+state
- Pinecone for vector DB
- tweepy+farcaster-py for social media
- Telegram for prod/dev notifications (bugs etc)
- freeGPT API for knowledge (maybe?)


# Inspirations

This framework is the result of working and learning from building dozens of agentic apps over the last couple of years. Of all frameworks, one specifically stood out to me: FinMem, based on the paper [FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design](https://arxiv.org/abs/2311.13743)

I've used langchain, llama-index, played with Virtual Protocol's Game. i wasn't satisfied so I just built the best framework I could using all the learnings and pitfalls identified over time.
