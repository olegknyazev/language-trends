import itertools
from . import github
from . import data

def scan_commits(language, max_repos=-1, max_days=-1):
  for repo_id, repo_name in _take(github.fetch_repos(language), max_repos):
    data.store_repo(repo_id, repo_name, language)
    all_commits = github.fetch_commits(repo_id)
    commits_by_day = itertools.groupby(all_commits, key=lambda dt: dt.date())
    for date, commits in _take(commits_by_day, max_days):
      data.store_commits(repo_id, date, sum(1 for c in commits))

def _take(iter, num):
  return itertools.islice(iter, num) if num >= 0 else iter
