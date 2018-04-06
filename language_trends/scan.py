import asyncio
import time

from dateutil.parser import parse as parse_date

from .github import Session as GitHubSession
from .languages import ALL_LANGUAGES
from .asyncutil import for_each_parallel
from . import data

MAX_PARALLEL_REPOS = 4

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
  repos_scanned = 0
  total_commits = 0

  async def status():
    nonlocal repos_scanned
    nonlocal total_commits
    last_repos_scanned = 0
    last_time = time.perf_counter()
    while True:
      await asyncio.sleep(3)
      now = time.perf_counter()
      time_elapsed = now - last_time
      last_time = now
      repos_per_second = (repos_scanned - last_repos_scanned) / time_elapsed
      log('  Scanning {}: {} repos, {} commits, {} repos/sec.'.format(
        language, repos_scanned, total_commits, repos_per_second))
      last_repos_scanned = repos_scanned

  async def process_repo(repo):
    commits = (
      await github.fetch_commits_monthly_breakdown(
        repo['id'],
        since=parse_date(repo['createdAt']),
        until=parse_date(repo['pushedAt'])))
    update_repo(repo, commits)

  def update_repo(repo, commits):
    nonlocal repos_scanned
    nonlocal total_commits
    commits = list(commits)
    data.store_repo(repo['id'], repo['name'], language)
    data.store_commits(repo['id'], commits)
    repos_scanned += 1
    total_commits += sum(x[1] for x in commits)

  if log is not None:
    log('Scanning ' + language)
    loop = asyncio.get_event_loop()
    status_task = loop.create_task(status())

  async with GitHubSession() as github:
    repos = github.fetch_repos(language, ['id', 'name', 'createdAt', 'pushedAt'])
    await for_each_parallel(repos, process_repo, MAX_PARALLEL_REPOS)

  if log is not None:
    status_task.cancel()

def update_aggregated_data():
  data.update_aggregated_data()

def main():
  try:
    update_language('clojure', log=print)
  except KeyboardInterrupt:
    pass
  update_aggregated_data()

if __name__ == '__main__':
  main()
