import requests
import os.path
import functools
import dateutil.parser
import string
import datetime

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'
PAGE_SIZE = 100

def repo_count(language):
  result = _query(string.Template(r'''{
      $search {
        repositoryCount
      }}''').substitute(search=_search_clause(language)))
  return _getin(result, 'data', 'search', 'repositoryCount')

def fetch_repos(language):
  """Yields all the repositories in the form (id, name) for the provided language."""
  cursor = None
  has_next_page = True
  while has_next_page:
    result = _query(string.Template(r'''{
        $search {
          nodes {
            ... on Repository {
              id
              name }}
          pageInfo {
            endCursor
            hasNextPage }}}''').substitute(
              search=_search_clause(language, PAGE_SIZE, cursor)))
    search = _getin(result, 'data', 'search')
    nodes = _getin(search, 'nodes')
    for node in nodes:
      yield node['id'], node['name']
    cursor = _getin(search, 'pageInfo', 'endCursor')
    has_next_page = _getin(search, 'pageInfo', 'hasNextPage')

def fetch_commits(repo_id, since=None):
  """Yields all the commits from the repository specified by repo_id, starting
  from the most recent one.
  """
  since = since.isoformat() if isinstance(since, datetime.datetime) else since
  cursor = None
  has_next_page = True
  since_clause = f', since: "{since}"' if since is not None else ''
  while has_next_page:
    result = _query(string.Template(r'''{
      node(id: "$id") {
        ... on Repository {
          defaultBranchRef {
            target {
              ... on Commit {
                history($page_clause $since_clause) {
                  nodes {
                    committedDate }
                  pageInfo {
                    endCursor
                    hasNextPage }}}}}}}}''').substitute(
                      id=repo_id,
                      since_clause=since_clause,
                      page_clause=', '.join(_pagination_clauses(PAGE_SIZE, cursor))))
    history = _getin(result, 'data', 'node', 'defaultBranchRef', 'target', 'history')
    for commit in history['nodes']:
      yield dateutil.parser.parse(commit['committedDate'])
    cursor = _getin(history, 'pageInfo', 'endCursor')
    has_next_page = _getin(history, 'pageInfo', 'hasNextPage')

def _getin(obj, *path):
  return functools.reduce(lambda obj, seg: obj[seg], path, obj)

def _pagination_clauses(first=None, after=None):
  result = []
  if first is not None: result.append(f'first: {first}')
  if after is not None: result.append(f'after: "{after}"')
  return result

def _search_clause(language, first=None, after=None):
  extra = ''.join(', ' + c for c in _pagination_clauses(first, after))
  return fr'search(query: "language:{language} size:>=10000", type: REPOSITORY {extra})'

def _query(query):
  return requests.post(
      SERVICE_END_POINT,
      json = {'query': query},
      headers = _auth_headers()
    ).json()

_cached_auth_token = None

def _auth_token():
  global _cached_auth_token
  if _cached_auth_token is None:
    if os.path.isfile(AUTH_TOKEN_FILENAME):
      with open(AUTH_TOKEN_FILENAME) as f:
        _cached_auth_token = f.read().strip()
  return _cached_auth_token

def _auth_headers():
  token = _auth_token()
  if not token:
    raise Exception(
      f"Authorization token isn't found." +
      f"Be sure that file {AUTH_TOKEN_FILENAME} exists.")
  return {'Authorization': 'bearer ' + token}
