import asyncio
from itertools import groupby
from datetime import datetime, time
from . import github
from . import data

MAX_PARALLEL_REPOS = 4

async def _should_update(language):
  scanned = data.repo_count(language)
  total = await github.repo_count(language)
  return scanned < total

async def _update_impl(language='clojure', log=None):
  if await _should_update(language):
    await _for_each_parallel(
      github.fetch_repos(language),
      lambda r: _update_repo_commits(*r, language, log=log),
      max_parallelism=MAX_PARALLEL_REPOS)

async def _update_repo_commits(repo_id, repo_name, language, log=None):
  last_commit = data.last_commit_date(repo_id)
  if last_commit is None:
    data.store_repo(repo_id, repo_name, language)
  else:
    last_commit = datetime.combine(last_commit, time.min)
  new_commits = [x async for x in github.fetch_commits(repo_id, since=last_commit)]
  new_commits.sort(key=lambda dt: dt.date())
  commits_by_day = groupby(new_commits, key=lambda dt: dt.date())
  records = [(date, sum(1 for x in commits)) for date, commits in commits_by_day]
  data.store_commits(repo_id, records)
  if log is not None:
    log(f'Processed {repo_name}: {len(records)} days, {sum(r[1] for r in records)} commits')

async def _for_each_parallel(aiter, process, max_parallelism):
  tasks = {}
  async def execute(k):
    await process(k)
    return k
  async for x in aiter:
    tasks[x] = asyncio.get_event_loop().create_task(execute(x))
    if len(tasks) >= max_parallelism:
      finished = await next(asyncio.as_completed(tasks.values()))
      tasks.pop(finished)
  await asyncio.gather(*tasks.values())

def update(language='clojure', log=None):
  loop = asyncio.get_event_loop()
  loop.run_until_complete(
    loop.create_task(
      _update_impl(language=language, log=log)))

if __name__ == '__main__':
  update(log=print)
