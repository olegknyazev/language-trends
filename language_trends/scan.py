import itertools
from . import github
from . import data

def scan_commits(language):
  """Returns an iterator yielding actions that should be performed to make
  the database reflect the current GitHub state.
  """
  for repo_id, repo_name in github.fetch_repos(language):
    yield lambda: data.store_repo(repo_id, repo_name, language)
    all_commits = github.fetch_commits(repo_id)
    for date, commits in itertools.groupby(all_commits, key=lambda dt: dt.date()):
      yield lambda: data.store_commits(repo_id, date, sum(1 for c in commits))

def perform(actions):
  for a in actions:
    a()
