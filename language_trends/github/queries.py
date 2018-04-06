import string
from datetime import datetime

PAGE_SIZE = 100

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
                        search=_search_clause(language, first=100, **search_args),
                        repository_fields=' '.join(repository_fields),
                        commit_fields=' '.join(commit_fields),
                        history_args=_join_args(_pagination_args(first=5))
                      )

REPOS_BASE_PATH = ['data', 'search']

def repos(language, fields, cursor=None):
  return string.Template(r'''{
      $search {
        nodes {
          ... on Repository {
            $fields }}
        pageInfo {
          endCursor
          hasNextPage }}}''').substitute(
            fields=' '.join(fields),
            search=_search_clause(language, first=PAGE_SIZE, after=cursor))

COMMITS_BASE_PATH = ['data', 'node', 'defaultBranchRef', 'target', 'history']

def commits(repo_id, fields, since=None, cursor=None):
  history_args = {}
  if since is not None:
    history_args['since'] = f'"{_fmt_date(since)}"'
  history_args.update(_pagination_args(first=PAGE_SIZE, after=cursor))
  return string.Template(r'''{
      node(id: "$id") {
        ... on Repository {
          defaultBranchRef {
            target {
              ... on Commit {
                history($history_args) {
                  nodes {
                    $fields }
                  pageInfo {
                    endCursor
                    hasNextPage }}}}}}}}''').substitute(
                      id=repo_id,
                      fields=' '.join(fields),
                      history_args=_join_args(history_args))

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

def _join_args(args): return ', '.join(f'{k}: {v}' for k, v in args.items())

def _fmt_date(date):
  return date.isoformat() if isinstance(date, datetime) else date

