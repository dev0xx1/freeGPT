from freegpt.ai.ai_models import llm_completion
from freegpt.clients import langfuse_client


async def generate_post(user_prompt):
    system_prompt = langfuse_client.get_prompt('persona').compile()
    task_prompt = langfuse_client.get_prompt('generate_post').compile()

    llm_response = await llm_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        task_prompt=task_prompt,
        model="azure/gpt-4o",
        temperature=0.6,
    )

    return llm_response