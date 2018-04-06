import asyncio

async def for_each_parallel(aiter, process, max_parallelism):
  tasks = {}
  async def execute(item):
    await process(item)
    return id(item)
  async for item in aiter:
    tasks[id(item)] = asyncio.get_event_loop().create_task(execute(item))
    if len(tasks) >= max_parallelism:
      finished = await next(asyncio.as_completed(tasks.values()))
      tasks.pop(finished)
  await asyncio.gather(*tasks.values())
