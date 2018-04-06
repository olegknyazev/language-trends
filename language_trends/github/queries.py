import string
from datetime import datetime

MAX_PAGE_SIZE = 100

REPO_COUNT_PATH = ['data', 'search', 'repositoryCount']

def repo_count(language, **search_args):
  return string.Template(r'''{
      $search {
        repositoryCount
      }}''').substitute(search=_search_clause(language, **search_args))

REPOS_WITH_COMMITS_REPO_PATH = ['data', 'search', 'nodes']
REPOS_WITH_COMMITS_COMMITS_PATH = ['defaultBranchRef', 'target', 'history', 'nodes']

def repos_with_commits(language, repository_fields, commit_fields, **search_args):
  return string.Template(r'''{
      $search {
        nodes {
          ... on Repository {
            $repository_fields
            defaultBranchRef {
              target {
                ... on Commit {
                  history($history_args) {
                    nodes {
                      $commit_fields }}}}}}}}}''').substitute(
                        search=_search_clause(language, first=MAX_PAGE_SIZE, **search_args),
                        repository_fields=' '.join(repository_fields),
                        commit_fields=' '.join(commit_fields),
                        history_args=_join_args(_pagination_args(first=5))
                      )

def _pagination_args(first=None, after=None):
  result = {}
  if first is not None: result['first'] = first
  if after is not None: result['after'] = f'"{after}"'
  return result

def _search_clause(language, *, first=None, after=None, created_range=None, pushed_range=None):
  args = {}
  args.update(_search_args(language, created_range=created_range, pushed_range=pushed_range))
  args.update(_pagination_args(first, after))
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

