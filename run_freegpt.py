import asyncio

from data_samples.zerohedge_article import zerohedge_sample_article
from archive.freegpt import Brain
from archive.freegpt import langfuse_client

from archive.freegpt import Environment
from archive.freegpt import FreeGPT

reflections_task = ''


class CustomEnvironment(Environment):

    async def fetch_context(self):
        return zerohedge_sample_article


environment = CustomEnvironment(
    update_environment_prompt=langfuse_client.get_prompt("persona_freegpt").compile()
)
brain = Brain(
    reflections_prompt=langfuse_client.get_prompt("reflections_task").compile()
)

freegpt_agent = FreeGPT(
    environment=environment,
    brain=brain,
)

async def main():

    while True:

        await freegpt_agent.step()
        await asyncio.sleep(1)

if __name__ == '__main__':

    asyncio.run(main())