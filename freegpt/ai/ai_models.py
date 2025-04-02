import json
from json import JSONDecodeError
from typing import Dict, Any

import httpx
import litellm
from langfuse.decorators import observe, langfuse_context
from litellm import acompletion, Timeout, APIConnectionError, RateLimitError
from litellm.llms.vertex_ai.common_utils import VertexAIError
from pydantic import BaseModel
from pydantic_core import ValidationError
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential

from archive.freegpt.llms.helpers import convert_pydantic_to_openai_function


class AIModelResponse(BaseModel):
    raw: Dict
    processed: Any
    trace_url: str


@observe(as_type='generation')
@retry(
    reraise=True,
    stop=stop_after_attempt(10),
    wait=wait_exponential(min=1, max=60),
    retry=retry_if_exception_type(
        (litellm.exceptions.InternalServerError,
         APIConnectionError, JSONDecodeError, ValidationError, Timeout, httpx.ReadTimeout, VertexAIError,
         RateLimitError))
)
async def llm_completion(
        system_prompt,
        user_prompt,
        task_prompt=None,
        model='azure/gpt-4o-mini',
        temperature=0,
        response_model=None,
        max_tokens=1500,
        timeout=60,
        observation_name='llm_call',
):
    langfuse_context.update_current_observation(
        name=observation_name,
        model=model,
        model_parameters={
            'temperature': temperature,
        },
    )
    # Format messages
    messages = [
                   {
                       "role": "system",
                       "content": system_prompt + (task_prompt or '')
                   }] + [
                   {
                       "role": "user",
                       "content": user_prompt
                   }
               ]

    completion = await acompletion(
        messages=messages,
        model=model,
        temperature=temperature,
        top_p=1,
        max_tokens=max_tokens,
        timeout=timeout,
        response_format=response_model or None,
    )

    llm_output_content = completion.choices[0].message.content
    if response_model:
        llm_output_content = response_model(**json.loads(llm_output_content))

    return AIModelResponse(
        raw=completion.to_dict(),
        processed=llm_output_content,
        trace_url=langfuse_context.get_current_trace_url()
    )


@observe(as_type='generation')
@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(min=1, max=60),
    retry=retry_if_exception_type(
        (APIConnectionError, JSONDecodeError, ValidationError, Timeout, httpx.ReadTimeout, VertexAIError))
)
async def llm_tool_call(
        user_content,
        stop_tool_names,
        system_prompt=None,
        task_prompt=None,
        model='azure/gpt-4o-mini',
        temperature=0,
        max_tokens=1500,
        timeout=60,
        observation_name='call_agent',
        tools=[],
):
    langfuse_context.update_current_observation(
        name=observation_name,
        model=model,
        model_parameters={
            'temperature': temperature,
        },
    )

    # Format messages
    tools = [convert_pydantic_to_openai_function(tool) for tool in tools]

    messages = [
                   {
                       "role": "system",
                       "content": system_prompt + (task_prompt or '')
                   }] + [
                   {
                       "role": "user",
                       "content": user_content
                   }
               ]

    max_rounds = 10
    i = 0

    while True:

        i + 1
        if i > max_rounds:
            return "sorry i bugged out"

        if 'tool_call_id' in messages[-1]:
            messages[0]['content'] = system_prompt

        completion = await acompletion(
            messages=messages,
            model=model,
            temperature=temperature,
            top_p=1,
            max_tokens=max_tokens,
            tool_choice="required",
            tools=tools,
            timeout=timeout
        )

        messages.append(
            completion.choices[0].message.model_dump()
        )

        for tool_call in completion.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # EXIT CONDITION
            if function_name in stop_tool_names:
                return function_args['text']
            else:
                tool = [i for i in tools if i.__name__ == function_name][0]
                if not tool:
                    return "Tool not found"
                tool_response = await tool.run_tool(**function_args)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": tool_response,
            })


async def run_llm_call():
    ai_models = AIModels()

    response = await ai_models.llm_completion(
        system_prompt="You are a helpful assistant.",
        user_prompt="Whats your name",
        model='azure/gpt-4o-mini',
        temperature=0,
        max_tokens=1500,
        timeout=60,
    )

    print(response)


async def run_tool_call():

    response = await llm_completion(
        system_prompt="You are a helpful assistant.",
        user_prompt="Whats your name",
        model='azure/gpt-4o-mini',
        temperature=0,
        max_tokens=1500,
        timeout=60,
    )

    print(response)


if __name__ == '__main__':
    import asyncio

    asyncio.run(run_llm_call())
