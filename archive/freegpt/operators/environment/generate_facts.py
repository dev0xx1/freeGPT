from typing import List

from pydantic import BaseModel, Field

from archive.freegpt.ai.ai_models import llm_completion

# STATE
class Fact(BaseModel):
    content: str = Field(..., description="Content of the fact")


class Facts(BaseModel):
    facts: List[Fact]

async def generate_facts(freegpt_agent, context: str):
    new_facts = await llm_completion(
        system_prompt=freegpt_agent.persona_prompt,
        task_prompt=freegpt_agent.update_environment_task_prompt,
        user_prompt=context,
        response_model=Facts
    )
    return new_facts