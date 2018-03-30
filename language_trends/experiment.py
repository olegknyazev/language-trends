import asyncio

async def interposed(*l):
  for x in l:
    await asyncio.sleep(0.5)
    yield x

def fetch_repos():
  return interposed('repo1', 'repo2', 'repo3', 'repo4', 'repo5')

async def fetch_commits(repo):
  for n in range(20):
    yield '{}_c{:2}'.format(repo, n)
    if n % 5 == 4:
      await asyncio.sleep(0.5)

async def process_repo(r):
  async for c in fetch_commits(r):
    print(c)
  return r

async def experiment_impl_serial():
  async for r in fetch_repos():
    await process_repo(r)

async def experiment_impl_parallel():
  tasks = {}
  async for r in fetch_repos():
    tasks[r] = asyncio.get_event_loop().create_task(process_repo(r))
    if len(tasks) >= 2:
      finished = await next(asyncio.as_completed(tasks.values()))
      tasks.pop(finished)
  await asyncio.gather(*tasks.values())

def experiment():
  loop = asyncio.get_event_loop()
  loop.run_until_complete(loop.create_task(experiment_impl_parallel()))

if __name__ == '__main__':
  experiment()
