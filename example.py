import asyncio
from freegpt.agent import FreeGPT
from freegpt.constants import langfuse_client

async def fetch_context_lambda():
    example = """
Today, xAI and X have merged into a single entity as per Elon Musks announcement on his X account        
"""
    return example


# LOAD PROMPTS
persona_prompt = langfuse_client.get_prompt("persona").compile()
update_environment_task_prompt =  langfuse_client.get_prompt("update_environment_task").compile()


freegpt_agent = FreeGPT(
    name="FreeGPT",
    fetch_context_lambda=fetch_context_lambda,
)


async def main():

    while True:

        await freegpt_agent.step()
        await asyncio.sleep(1)

if __name__ == '__main__':

    asyncio.run(main())