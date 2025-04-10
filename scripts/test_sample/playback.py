from freegpt.agent.generate_post import generate_post
import asyncio

from scripts.test_sample.dataset import EXAMPLE_2, EXAMPLE_1


async def run_dataset():
    """
    """
    # TODO Add 1 liner examples
    # TODO Add url embed

    print("STARTING MEME GENERATION")

    import datetime

    for model in ['gemini/gemini-1.5-pro']:
        results = await asyncio.gather(generate_post(EXAMPLE_1,
                                                     model=model),
                                       generate_post(EXAMPLE_2,
                                                     model=model))

        print(f"\n\n\nMODEL: {model}")
        print(f"{datetime.datetime.now()}")
        print(f"MEME 1:\n{results[0][0]}\n\n")
        print(f"MEME 2:\n{results[1][0]}")


meme = asyncio.run(
    run_dataset()
)
