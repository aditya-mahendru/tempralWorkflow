import asyncio, random

async def flaky_call() -> None:
    rand_num = random.random()
    if rand_num < 0.33:
        raise RuntimeError("Forced failure for testing")

    if rand_num < 0.67:
            await asyncio.sleep(300)  # Expect the activity layer to time out before this completes
		
