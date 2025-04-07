import pprint

from freegpt.ai.ai_models import llm_completion
from freegpt.clients import langfuse_client


async def generate_post(past_posts):
    system_prompt = langfuse_client.get_prompt('persona').compile()
    task_prompt = langfuse_client.get_prompt('generate_post').compile()

    user_prompt = f"""
<PAST POSTS>
{past_posts}
</PAST POSTS>
"""

    llm_response = await llm_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        task_prompt=task_prompt,
        model="azure/gpt-4o",
        temperature=0.6,
        observation_name='generate_post',
    )

    return llm_response