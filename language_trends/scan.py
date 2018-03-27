import itertools
import datetime
from . import github
from . import data

def should_update(language):
  scanned = data.repo_count(language)
  total = github.repo_count(language)
  return scanned < total

def update(language='clojure'):
  if should_update(language):
    for repo_id, repo_name in github.fetch_repos(language):
      last_commit = data.last_commit_date(repo_id)
      if last_commit is None:
        data.store_repo(repo_id, repo_name, language)
      else:
        last_commit = datetime.datetime.combine(last_commit, datetime.time.min)
      commits_since_last = github.fetch_commits(repo_id, since=last_commit)
      commits_by_day = itertools.groupby(commits_since_last, key=lambda dt: dt.date())
      records = [(date, sum(1 for c in commits)) for date, commits in commits_by_day]
      data.store_commits(repo_id, records)
      print(f'PROCESSED {repo_name}, {len(records)} days, {sum(r[1] for r in records)} commits')

def scan_commits(language, max_repos=-1, max_days=-1):
  for repo_id, repo_name in _take(github.fetch_repos(language), max_repos):
    data.store_repo(repo_id, repo_name, language)
    all_commits = github.fetch_commits(repo_id)
    commits_by_day = itertools.groupby(all_commits, key=lambda dt: dt.date())
    for date, commits in _take(commits_by_day, max_days):
      data.store_commits(repo_id, date, sum(1 for c in commits))

def _take(iter, num):
  return itertools.islice(iter, num) if num >= 0 else iter

if __name__ == '__main__':
  update()
