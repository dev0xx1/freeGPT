import asyncio

from freegpt.ai.ai_models import llm_completion
from freegpt.clients import langfuse_client
from freegpt.helpers import process_post



async def generate_post(user_prompt,
                        system_prompt,
                        task_prompt,
                        model="azure/gpt-4o",
                        temperature=0.6):
    llm_response = await llm_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        task_prompt=task_prompt,
        model=model,
        temperature=temperature,
    )
    llm_output_content = llm_response.processed
    parsed_post = llm_output_content.split('<post>')[1].split('</post>')[0].strip()
    parsed_post = process_post(parsed_post)
    return parsed_post


async def select_best_meme(suggestions):
    # Step 2: Run the selection/refinement prompt
    writing_style_prompt = langfuse_client.get_prompt('writing_style').compile()
    system_prompt = langfuse_client.get_prompt('persona').compile()
    task_prompt = langfuse_client.get_prompt('select_meme').compile(writing_style=writing_style_prompt)

    llm_response = await llm_completion(
        system_prompt=system_prompt,
        user_prompt='Meme suggestion:\n' + '\n'.join(suggestions),
        task_prompt=task_prompt,
        model='xai/grok-2-latest',
        temperature=0,
    )

    parsed_post = llm_response.processed.split('<final_post>')[1].split('</final_post>')[0].strip()
    parsed_post = process_post(parsed_post)
    return parsed_post


async def generate_viral_meme(context):
    models = ['gemini/gemini-1.5-pro', 'azure/gpt-4o', 'xai/grok-2-latest']
    system_prompt = langfuse_client.get_prompt('persona').compile()
    writing_style_prompt = langfuse_client.get_prompt('writing_style').compile()
    task_prompt = langfuse_client.get_prompt('generate_post').compile(writing_style=writing_style_prompt)

    # Step 1: Parallelize meme generation
    tasks = [
        generate_post(user_prompt=context,
                      system_prompt=system_prompt,
                      task_prompt=task_prompt,
                      model=model,
                      temperature=0.5)
        for model in models
    ]
    suggestions = await asyncio.gather(*tasks)
    best_meme = await select_best_meme(suggestions)
    return best_meme

