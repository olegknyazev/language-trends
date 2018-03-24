import itertools
from . import github
from . import data

def scan_repositories(language):
  for repo_id, repo_name in github.fetch_repos(language):
    data.store_repo(repo_id, repo_name, language)
    all_commits = github.fetch_commits(repo_id)
    for date, commits in itertools.groupby(all_commits, key=lambda dt: dt.date()):
      data.store_commits(repo_id, date, sum(1 for c in commits))
