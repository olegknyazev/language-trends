import requests
import os.path
import functools
import dateutil.parser
import string

from . import queries

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'

def repo_count(language):
  result = _query(queries.repo_count(language))
  return _getin(result, *queries.REPO_COUNT_PATH)

def fetch_repos(language):
  """Yields all the repositories in the form (id, name) for the provided language."""
  pages = _fetch_paginated(
    lambda c: queries.repos(language, ['id', 'name'], cursor=c),
    [*queries.REPOS_BASE_PATH, 'pageInfo'])
  for page in pages:
    for node in _getin(page, *queries.REPOS_BASE_PATH, 'nodes'):
      yield node['id'], node['name']

def fetch_commits(repo_id, since=None):
  """Yields all the commits from the repository specified by repo_id, starting
  from the most recent one.
  """
  pages = _fetch_paginated(
    lambda c: queries.commits(repo_id, ['committedDate'], since=since, cursor=c),
    [*queries.COMMITS_BASE_PATH, 'pageInfo'])
  for page in pages:
    for commit in _getin(page, *queries.COMMITS_BASE_PATH, 'nodes'):
      yield dateutil.parser.parse(commit['committedDate'])

def _fetch_paginated(make_query, page_info_path):
  cursor = None
  has_next_page = True
  while has_next_page:
    result = _query(make_query(cursor))
    yield result
    cursor = _getin(result, *page_info_path, 'endCursor')
    has_next_page = _getin(result, *page_info_path, 'hasNextPage')

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
