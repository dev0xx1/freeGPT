from abc import abstractmethod
from typing import List

from pydantic import BaseModel, Field

from freegpt.llms.base import call_llm


# STATE
class Story(BaseModel):
    content: str = Field(..., description="Content of the story")

class Stories(BaseModel):
    stories: List[Story]


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
        new_stories = await self.generate_stories(context)

        # save embeddings
        await self.save_stories(new_stories)
        await self.save_embeddings(new_stories)
        
        relevant_stories = await self.fetch_relevant_stories()
        
        return relevant_stories


    async def generate_stories(self, context):
        new_stories = await call_llm(
            system_content=self.persona_prompt,
            task=self.update_environment_prompt,
            user_content=context,
            response_model=Stories
        )
        return new_stories


    async def save_stories(self, new_stories):
        return


    async def save_embeddings(self,
                              stories):
        # Generate embeddings
        # Store in chroma DB
        
        return
    
    
    async def fetch_relevant_stories(self):
        return