import asyncio

from langfuse.decorators import observe

from freegpt.agent.ai_models import llm_completion
from freegpt.clients import langfuse_client
from freegpt.helpers import process_post, run_punchline_algorithm


async def generate_post(context,
                        model="azure/gpt-4o",
                        temperature=0.6):

    punchline_structure = run_punchline_algorithm()
    system_prompt = langfuse_client.get_prompt('persona').compile()
    task_prompt = langfuse_client.get_prompt('generate_post').compile(punchline_structure=punchline_structure)

    llm_response = await llm_completion(
        system_prompt=system_prompt,
        user_prompt=context,
        task_prompt=task_prompt,
        model=model,
        temperature=temperature,
    )
    llm_output_content = llm_response.processed
    parsed_post = llm_output_content.split('<final_post>')[1].split('</final_post>')[0].strip()
    parsed_post = process_post(parsed_post)
    return parsed_post, llm_response.trace_url


async def select_best_meme(suggestions):
    # Step 2: Run the selection/refinement prompt
    writing_style_prompt = langfuse_client.get_prompt('writing_style').compile()
    system_prompt = langfuse_client.get_prompt('persona').compile()
    task_prompt = langfuse_client.get_prompt('select_meme').compile(writing_style=writing_style_prompt)

    llm_response = await llm_completion(
        system_prompt=system_prompt,
        user_prompt='[Meme suggestion]:\n'.join(suggestions),
        task_prompt=task_prompt,
        model='xai/grok-3-latest',
        temperature=0,
    )

    parsed_post = llm_response.processed.split('<final_post>')[1].split('</final_post>')[0].strip()
    parsed_post = process_post(parsed_post)
    return parsed_post, llm_response.trace_url
