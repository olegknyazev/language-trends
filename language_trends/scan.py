import asyncio
import time

from .github import Session as GitHubSession, BEGIN_OF_TIME
from .languages import ALL_LANGUAGES
from .asyncutil import for_each_parallel
from .months import first_day_of_month
from . import data
from . import util

MAX_PARALLEL_REPOS = 10

def update(langs, log=print):
  loop = asyncio.get_event_loop()
  for lang in langs:
    loop.run_until_complete(_update_impl(lang, log=log))
  loop.close()

def update_aggregated_data():
  data.update_aggregated_data()

def main(args):
  langs = args if args else ALL_LANGUAGES
  try:
    update(langs, log=print)
  except KeyboardInterrupt:
    pass
  update_aggregated_data()

async def _update_impl(lang, log=print):
  until = util.current_date()
  current_month = first_day_of_month(until)
  actual_by = data.lang_actual_by(lang)

  log(f'Updating {lang}')
  if not actual_by:
    log('  Language had never been scanned, performing a full scan')
    await _scan_github(
      lang,
      until=util.as_datetime(current_month),
      log=log)
  elif actual_by < current_month:
    log(f'  Language is actual by {actual_by}, but now is {current_month}')
    log(f'  Performing an incremental scan')
    await _scan_github(
        lang,
        since=util.as_datetime(actual_by),
        until=util.as_datetime(current_month),
        skip_existing=False,
        log=log)
  else:
    log(f'  Language is actual')

  data.store_lang_scan(lang, actual_by=current_month)

async def _scan_github(lang, since=None, until=None, skip_existing=True, log=print):
  since = since or BEGIN_OF_TIME
  until = until or util.current_date()

  repos_total = 0
  repos_scanned = 0
  repos_skipped = 0
  total_commits = 0

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
        status_string = '  Rate limited, waiting for some time...'
      elif github.abuse_detected:
        status_string = '  Abuse detected, waiting for some time...'
      else:
        status_string = (
          f'  {lang}:' +
          f' {repos_scanned} scanned,' +
          f' {repos_skipped} skipped' +
         (f' ({repos_processed} / {repos_total}, {int(repos_processed / repos_total * 100)}%),'
            if repos_total else '') +
          f' {total_commits} commits,' +
          f' {repos_per_second:.3} repos/sec.,' +
          f' {requests_per_second:.3} req./sec.')
      if status_string != last_status_string:
        log(status_string)
        last_status_string = status_string
      last_repos_processed = repos_processed
      last_requests_sent = github.requests_sent

  async def process_repo(repo):
    nonlocal repos_skipped
    if skip_existing and data.is_repo_exists(repo['id']):
      repos_skipped += 1
      return
    commits = (
      await github.fetch_commits_monthly_breakdown(
        repo['id'],
        since=max((since, repo['createdAt'])),
        until=min((until, repo['pushedAt']))))
    update_repo(repo, commits)

  def update_repo(repo, commits):
    nonlocal repos_scanned
    nonlocal total_commits
    commits = list(commits)
    data.store_repo(repo['id'], repo['name'], lang)
    data.store_commits(repo['id'], commits)
    repos_scanned += 1
    total_commits += sum(x[1] for x in commits)

  status_task = asyncio.ensure_future(print_status_periodically())
  try:
    async with GitHubSession() as github:
      repos_total = (
        await github.repo_count(
          lang,
          created_range=(BEGIN_OF_TIME, until),
          pushed_after=since))
      repos = (
        github.fetch_repos(
          lang,
          ['id', 'name', 'createdAt', 'pushedAt'],
          pushed_after=since,
          until=until))
      await for_each_parallel(repos, process_repo, MAX_PARALLEL_REPOS)
  finally:
    status_task.cancel()

if __name__ == '__main__':
  import sys
  main(sys.argv[1:])

