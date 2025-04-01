import json
from json import JSONDecodeError
from typing import Type, List, Union, Optional

import httpx
import litellm
from langfuse.decorators import observe, langfuse_context
from litellm import acompletion, Timeout, APIConnectionError, RateLimitError
from pydantic import BaseModel, field_validator, Field
from pydantic_core import ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, wait_exponential
from  litellm.llms.vertex_ai.common_utils import VertexAIError

from freegpt.llms.helpers import convert_pydantic_to_openai_function


@observe(as_type='generation')
@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(min=1, max=60),
    retry=retry_if_exception_type(
        (APIConnectionError, JSONDecodeError, ValidationError, Timeout, httpx.ReadTimeout, VertexAIError))
)
async def call_tools(
              name,
              system_content=None,
              user_content=None,
              model='azure/gpt-4o-mini',
              temperature=0,
              max_tokens=1500,
              timeout=60,
              observation_name='call_agent',
              task=None,
              tools=[],
              exit_tool_name=None,
              ):
    langfuse_context.update_current_observation(
        name=observation_name,
        model=model,
        model_parameters={
            'temperature': temperature,
        },
    )
    langfuse_context.update_current_trace(
        name=name
    )

    # Format messages
    tools  = [convert_pydantic_to_openai_function(tool) for tool in tools]

    system_content = system_content or system_content
    system_content = system_content+(task or '')

    messages = [
                   {
                       "role": "system",
                       "content": system_content
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
            messages[0]['content'] = system_content

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
            if function_name == exit_tool_name:
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


@observe(as_type='span')
@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(min=1, max=60),
    retry=retry_if_exception_type(
        (litellm.exceptions.InternalServerError,
         APIConnectionError, JSONDecodeError, ValidationError, Timeout, httpx.ReadTimeout, VertexAIError, RateLimitError))
)
async def call_llm(system_content,
                   task,
                   user_content,
                   model='azure/gpt-4o-mini',
                   temperature=0,
                   response_model=None,
                   max_tokens=1500,
                   timeout=60,
                   return_full_response=False,
                   observation_name='call_agent_llm',
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
                       "content": system_content+task
                   }] + [
                   {
                       "role": "user",
                       "content": user_content
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

    llm_output_content =  completion.choices[0].message.content
    if response_model:
        llm_output_content = response_model(**json.loads(llm_output_content))


    if return_full_response:
        return llm_output_content, completion, langfuse_context.get_current_trace_url()
    else:
        return llm_output_content
