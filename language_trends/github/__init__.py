import requests
import os.path
import functools
import dateutil.parser
import string

from . import queries

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'

def repo_count(language):
  result = _query(string.Template(r'''{
      $search {
        repositoryCount
      }}''').substitute(search=queries.search_clause(language)))
  return _getin(result, 'data', 'search', 'repositoryCount')

def fetch_repos(language):
  """Yields all the repositories in the form (id, name) for the provided language."""
  cursor = None
  has_next_page = True
  while has_next_page:
    result = _query(queries.format_repos_query(language, cursor))
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
  cursor = None
  has_next_page = True
  while has_next_page:
    result = _query(queries.format_commits_query(repo_id, since=since, cursor=cursor))
    history = _getin(result, 'data', 'node', 'defaultBranchRef', 'target', 'history')
    for commit in history['nodes']:
      yield dateutil.parser.parse(commit['committedDate'])
    cursor = _getin(history, 'pageInfo', 'endCursor')
    has_next_page = _getin(history, 'pageInfo', 'hasNextPage')

def _getin(obj, *path):
  return functools.reduce(lambda obj, seg: obj[seg], path, obj)

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
