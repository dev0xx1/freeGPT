from typing import List

from freegpt.brain import Brain
from freegpt.environment import Environment
from freegpt.llms.base import call_tools


class FreeGPT:

    def __init__(self,
                 persona_prompt,
                 decision_prompt,
                 brain: Brain,
                 environment: Environment,
                 tools: List):
        self.persona_prompt = persona_prompt
        self.tools = tools
        self.brain = brain
        self.environment = environment
        self.decision_prompt = decision_prompt

    async def make_decision(self, reflections: List):
        await call_tools(
            system_content=self.persona_prompt,
            task=self.decision_prompt,
            user_content=reflections,
            tools=self.tools,
        )

    async def step(self):
        relevant_stories = await self.environment.update_environment()
        reflections = await self.brain.reflect(context=relevant_stories)
        await self.make_decision(reflections=reflections)