import string
from datetime import datetime

PAGE_SIZE = 100

REPO_COUNT_PATH = ['data', 'search', 'repositoryCount']

def repo_count(language):
  return string.Template(r'''{
      $search {
        repositoryCount
      }}''').substitute(search=_search_clause(language))

REPOS_BASE_PATH = ['data', 'search']

def repos(language, cursor=None):
  return string.Template(r'''{
      $search {
        nodes {
          ... on Repository {
            id
            name }}
        pageInfo {
          endCursor
          hasNextPage }}}''').substitute(
            search=_search_clause(language, first=PAGE_SIZE, after=cursor))

COMMITS_BASE_PATH = ['data', 'node', 'defaultBranchRef', 'target', 'history']

def commits(repo_id, since=None, cursor=None):
  history_args = {}
  if since is not None:
    if isinstance(since, datetime):
      since = since.isoformat()
    history_args['since'] = f'"{since}"'
  history_args.update(_pagination_args(first=PAGE_SIZE, after=cursor))
  return string.Template(r'''{
      node(id: "$id") {
        ... on Repository {
          defaultBranchRef {
            target {
              ... on Commit {
                history($history_args) {
                  nodes {
                    committedDate }
                  pageInfo {
                    endCursor
                    hasNextPage }}}}}}}}''').substitute(
                      id=repo_id,
                      history_args=_join_args(history_args))

def _pagination_args(first=None, after=None):
  result = {}
  if first is not None: result['first'] = first
  if after is not None: result['after'] = f'"{after}"'
  return result

def _search_clause(language, first=None, after=None):
  args = {}
  args.update(_search_args(language))
  args.update(_pagination_args(first, after))
  return f'search ({_join_args(args)})'

def _search_args(language):
  return {
    'query': f'"language:{language} size:>=10000"',
    'type': 'REPOSITORY'}

def _join_args(args): return ', '.join(f'{k}: {v}' for k, v in args.items())

