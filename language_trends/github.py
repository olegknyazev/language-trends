import requests
import os.path
import functools
import dateutil.parser
import string

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'

def repo_count(language):
  result = _query(string.Template(r'''{
      $search {
        repositoryCount
      }}''').substitute(search=_search_clause(language)))
  return _getin(result, 'data', 'search', 'repositoryCount')

def fetch_repos(language):
  """Yields all the repositories in the form (id, name) for the provided language."""
  cursor = None
  hasNextPage = True
  bucket_size = 20
  while hasNextPage:
    result = _query(string.Template(r'''{
        $search {
          nodes {
            ... on Repository {
              id
              name }}
          pageInfo {
            endCursor
            hasNextPage }}}''').substitute(
              search=_search_clause(language, bucket_size, cursor)))
    search = _getin(result, 'data', 'search')
    nodes = _getin(search, 'nodes')
    for node in nodes:
      yield node['id'], node['name']
    cursor = _getin(search, 'pageInfo', 'endCursor')
    hasNextPage = _getin(search, 'pageInfo', 'hasNextPage')

def fetch_commits(repo_id):
  """Yields all the commits from the repository specified by repo_id, starting
  from the most recent one.
  """
  result = _query(string.Template(r'''{
    node(id: "$id") {
      ... on Repository {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 20) {
                nodes {
                  committedDate }}}}}}}}''').substitute(id=repo_id))
  history = _getin(result, 'data', 'node', 'defaultBranchRef', 'target', 'history', 'nodes')
  for commit in history:
    yield dateutil.parser.parse(commit['committedDate'])

def _getin(obj, *path):
  return functools.reduce(lambda obj, seg: obj[seg], path, obj)

def _search_clause(language, first=None, after=None):
  c1 = f', first: {first}' if first is not None else ''
  c2 = f', after: "{after}"' if after is not None else ''
  return fr'search(query: "language:{language} size:>=1000", type: REPOSITORY {c1} {c2})'

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
