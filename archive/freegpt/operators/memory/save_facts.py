from archive.freegpt.agent import FreeGPT
from archive.freegpt.environment import Facts


async def save_facts_to_db(
        freegpt_agent: FreeGPT,
        facts: Facts
):

    # convert pydantic to SQLalchemy and insert
    return