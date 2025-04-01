import asyncio
import time

from freegpt.brain import Brain
from freegpt.constants import langfuse_client

from freegpt.environment import Environment
from freegpt.freegpt import FreeGPT

reflections_task = ''


class CustomEnvironment(Environment):

    async def fetch_context(self):
        # Add news fetching here
        return {}


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