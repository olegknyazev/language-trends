import asyncio
from aitertools import groupby
from datetime import datetime, time
from . import github
from . import data

async def _should_update(language):
  scanned = data.repo_count(language)
  total = await github.repo_count(language)
  return scanned < total

async def _update_impl(language='clojure', log=None):
  if await _should_update(language):
    async for repo_id, repo_name in github.fetch_repos(language):
      last_commit = data.last_commit_date(repo_id)
      if last_commit is None:
        data.store_repo(repo_id, repo_name, language)
      else:
        last_commit = datetime.combine(last_commit, time.min)
      commits_since_last = github.fetch_commits(repo_id, since=last_commit)
      commits_by_day = groupby(commits_since_last, key=lambda dt: dt.date())
      records = [(date, _count(commits)) async for date, commits in commits_by_day]
      data.store_commits(repo_id, records)
      if log is not None:
        log(f'Processed {repo_name}: {len(records)} days, {sum(r[1] for r in records)} commits')

async def _count(aiter):
  r = 0
  async for x in aiter:
    r += 1
  return r

def update(language='clojure', log=None):
  loop = asyncio.get_event_loop()
  loop.run_until_complete(
    loop.create_task(
      _update_impl(language=language, log=log)))

if __name__ == '__main__':
  update(log=print)
