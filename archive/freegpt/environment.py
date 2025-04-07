from abc import abstractmethod
from typing import List

from pydantic import BaseModel, Field


# STATE
class Fact(BaseModel):
    content: str = Field(..., description="Content of the fact")


class Facts(BaseModel):
    facts: List[Fact]


class Environment:

    def __init__(self,
                 persona_prompt: str,
                 update_environment_prompt):
        self.persona_prompt = persona_prompt
        self.update_environment_prompt = update_environment_prompt

    @abstractmethod
    async def fetch_context(self):
        return

    async def update_environment(self):

        # read news
        context = await self.fetch_context()

        # save stories
        new_facts = await self.generate_facts(context)

        # save embeddings
        await self.save_facts(new_facts)
        await self.save_embeddings(new_facts)

        relevant_stories = await self.fetch_relevant_stories()

        return relevant_stories


    async def save_facts(self, new_stories):


        return

    async def save_embeddings(self,
                              stories):
        # Generate embeddings
        # Store in chroma DB
        return

    async def fetch_relevant_stories(self):
        return