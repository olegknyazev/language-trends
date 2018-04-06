import string
from datetime import date, time, datetime

from language_trends.util import months

MAX_PAGE_SIZE = 100

REPO_COUNT_PATH = ['data', 'search', 'repositoryCount']
def repo_count(language, **search_args):
  return string.Template(r'''{
      $search {
        repositoryCount
      }}''').substitute(search=_search_clause(language, **search_args))

SEARCH_REPOS_BASE_PATH = ['data', 'search', 'nodes']
def search_repos(language, repository_fields, **search_args):
  return string.Template(r'''{
      $search {
        nodes {
          ... on Repository {
            $repository_fields }}}}''').substitute(
              search=_search_clause(language, **search_args),
              repository_fields=' '.join(repository_fields))

REPO_MONTHLY_TOTAL_COMMITS_BASE_PATH = ['data', 'node', 'defaultBranchRef', 'target']
def repo_monthly_total_commits(repo_id, since, until):
  return string.Template(r'''{
      node(id: "$repo_id") {
        ... on Repository {
          defaultBranchRef {
            target {
              ... on Commit {
                $history }}}}}}''').substitute(
                  repo_id=repo_id,
                  history=_history_clauses(since, until))

def _history_clauses(since, until):
  return '\n'.join(_commits_upto_clause(m) for m in months(since, until))

def _commits_upto_clause(date):
  return f'_{date.year}_{date.month}: history(until: "{_fmt_date(date)}") {{ totalCount }}'

def _search_clause(language, *, first=MAX_PAGE_SIZE, created_range=None, pushed_range=None):
  args = {'first': first}
  args.update(_search_args(language, created_range=created_range, pushed_range=pushed_range))
  return f'search ({_join_args(args)})'

def _search_args(language, *, created_range=None, pushed_range=None):
  def _time_range_args(action, range):
    return f'{action}:{_fmt_date(range[0])}..{_fmt_date(range[1])}' if range is not None else ''
  created = _time_range_args('created', created_range)
  pushed = _time_range_args('pushed', pushed_range)
  return {
    'query': f'"language:{language} size:>=10000 {created} {pushed}"',
    'type': 'REPOSITORY'}

def _join_args(args):
  return ', '.join(f'{k}: {v}' for k, v in args.items())

def _fmt_date(d):
  if isinstance(d, date):
    d = datetime.combine(d, time.min)
  return d.isoformat() if isinstance(d, datetime) else d

