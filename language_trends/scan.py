import asyncio
from itertools import groupby
from datetime import datetime, time

from .github import Session as GitHubSession
from .languages import ALL_LANGUAGES
from . import data

def update_all(log=None):
  loop = asyncio.get_event_loop()
  for lang in ALL_LANGUAGES:
    loop.run_until_complete(_update_impl(lang, log=log))
  loop.close()

def update_language(language, log=None):
  loop = asyncio.get_event_loop()
  loop.run_until_complete(_update_impl(language, log=log))
  loop.close()

async def _update_impl(language, log=None):
  async with GitHubSession() as github:
    async for repo_id, repo_name, commits in github.fetch_repos_with_commits(language):
      print(repo_id, repo_name, sum(1 for x in commits))

def update_aggregated_data():
  data.update_aggregated_data()

async def _should_update(github, language):
  scanned = data.repo_count(language)
  total = await github.repo_count(language)
  return scanned < total

async def _update_repo_commits(github, repo_id, repo_name, language, log=None):
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

def main():
  try:
    update_language('clojure')
  except KeyboardInterrupt:
    pass
  # update_aggregated_data()

if __name__ == '__main__':
  main()
