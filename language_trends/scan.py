import asyncio
import time

from .github import Session as GitHubSession
from .languages import ALL_LANGUAGES
from .asyncutil import for_each_parallel
from .months import first_day_of_month
from . import data
from . import util

MAX_PARALLEL_REPOS = 10

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
  repos_skipped = 0
  total_commits = 0
  until = util.current_date()

  async def print_status_periodically():
    nonlocal repos_scanned
    nonlocal repos_skipped
    nonlocal total_commits
    last_repos_processed = 0
    last_time = time.perf_counter()
    last_status_string = ''
    last_requests_sent = 0
    while True:
      await asyncio.sleep(3)
      now = time.perf_counter()
      time_elapsed = now - last_time
      last_time = now
      repos_processed = repos_scanned + repos_skipped
      repos_per_second = (repos_processed - last_repos_processed) / time_elapsed
      requests_per_second = (github.requests_sent - last_requests_sent) / time_elapsed
      if github.rate_limited:
        status_string = 'Rate limited, waiting for some time...'
      elif github.abuse_detected:
        status_string = 'Abuse detected, waiting for some time...'
      else:
        status_string = (
          '{}: {} scanned, {} skipped, {} commits, {:.3} repos/sec. {} req./sec.'.format(
            language,
            repos_scanned,
            repos_skipped,
            total_commits,
            repos_per_second,
            requests_per_second))
      if status_string != last_status_string:
        log(status_string)
        last_status_string = status_string
      last_repos_processed = repos_processed
      last_requests_sent = github.requests_sent

  async def process_repo(repo):
    nonlocal repos_skipped
    if data.is_repo_exists(repo['id']):
      repos_skipped += 1
      return
    commits = (
      await github.fetch_commits_monthly_breakdown(
        repo['id'],
        since=repo['createdAt'],
        until=min((until, repo['pushedAt']))))
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
    status_task = loop.create_task(print_status_periodically())

  async with GitHubSession() as github:
    repos = github.fetch_repos(language, ['id', 'name', 'createdAt', 'pushedAt'])
    await for_each_parallel(repos, process_repo, MAX_PARALLEL_REPOS)

  if log is not None:
    status_task.cancel()

  data.store_lang_scan(language, actual_by=first_day_of_month(until))

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

