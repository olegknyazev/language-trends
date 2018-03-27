from itertools import islice, groupby
from datetime import datetime, time
from . import github
from . import data

def should_update(language):
  scanned = data.repo_count(language)
  total = github.repo_count(language)
  return scanned < total

def update(language='clojure', log=None):
  if should_update(language):
    for repo_id, repo_name in github.fetch_repos(language):
      last_commit = data.last_commit_date(repo_id)
      if last_commit is None:
        data.store_repo(repo_id, repo_name, language)
      else:
        last_commit = datetime.combine(last_commit, time.min)
      commits_since_last = github.fetch_commits(repo_id, since=last_commit)
      commits_by_day = groupby(commits_since_last, key=lambda dt: dt.date())
      records = [(date, sum(1 for c in commits)) for date, commits in commits_by_day]
      data.store_commits(repo_id, records)
      if log is not None:
        log(f'Processed {repo_name}: {len(records)} days, {sum(r[1] for r in records)} commits')

if __name__ == '__main__':
  update(log=print)
