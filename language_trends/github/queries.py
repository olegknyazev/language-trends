import string
from datetime import datetime

MAX_PAGE_SIZE = 100

REPO_COUNT_PATH = ['data', 'search', 'repositoryCount']

def repo_count(language, **search_args):
  return string.Template(r'''{
      $search {
        repositoryCount
      }}''').substitute(search=_search_clause(language, **search_args))

SEARCH_REPOS_BASE_PATH = ['data', 'search', 'nodes']

# TODO PLAN:
#   1. repos_with_commits -> repos
#   2. add createdAt, pushedAt to its result
#   3. create separate repo_monthly_commits(id, start_month, end_month)

def search_repos(language, repository_fields, **search_args):
  return string.Template(r'''{
      $search {
        nodes {
          ... on Repository {
            $repository_fields }}}}''').substitute(
              search=_search_clause(language, **search_args),
              repository_fields=' '.join(repository_fields))

# REPOS_WITH_COMMITS_COMMITS_PATH = ['defaultBranchRef', 'target', 'history', 'nodes']
# def repo_monthly_commits():
#   '''
#             defaultBranchRef {
#               target {
#                 ... on Commit {
#                   history($history_args) {
#                     nodes {
#                       $commit_fields }}}}}
#   '''
#   pass

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

def _fmt_date(date):
  return date.isoformat() if isinstance(date, datetime) else date

