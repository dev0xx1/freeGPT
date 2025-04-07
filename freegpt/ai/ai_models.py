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
        model='azure/gpt-4o',
        temperature=0,
        response_model=None,
        max_tokens=1500,
        timeout=60,
        observation_name='llm_call',
) -> AIModelResponse:
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



