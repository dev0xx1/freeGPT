from typing import Callable

from archive.freegpt.constants import langfuse_client
from archive.freegpt.operators.environment.generate_facts import generate_facts


class FreeGPT:

    def __init__(self,
                 name,
                 fetch_context_lambda: Callable,
                 persona_prompt_name='persona',
                 update_environment_prompt_name='update_environment_task'):
        self.name = name
        self.fetch_context_lambda = fetch_context_lambda
        self.persona_prompt_name = persona_prompt_name
        self.update_environment_prompt_name = update_environment_prompt_name

    @property
    def persona_prompt(self):
        return langfuse_client.get_prompt(self.persona_prompt_name).compile()

    @property
    def update_environment_task_prompt(self):
        return langfuse_client.get_prompt(self.update_environment_prompt_name).compile()


    async def step(self):

        new_context = await self.fetch_context_lambda()
        generated_facts = await generate_facts(self, new_context)
