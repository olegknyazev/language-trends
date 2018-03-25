import requests
import os.path
import functools
import dateutil.parser

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'

def fetch_repos(language):
  """Yields all the repositories in the form (id, name) for the provided language."""
  def _after(cursor):
    return f', after: "{cursor}"' if cursor is not None else ""
  cursor = None
  exhausted = False
  bucket_size = 20
  while not exhausted:
    result = _query(r'''{
        search(query: "language:%s", type: REPOSITORY, first: %d %s) {
          edges {
            node {
              ... on Repository {
                id
                name }}
            cursor }}}''' % (language, bucket_size, _after(cursor)))
    edges = _getin(result, 'data', 'search', 'edges')
    retrieved = 0
    for e in edges:
      node = e['node']
      yield node['id'], node['name']
      cursor = e['cursor']
      retrieved += 1
    exhausted = retrieved < bucket_size

def fetch_commits(repo_id):
  """Yields all the commits from the repository specified by repo_id, starting
  from the most recent one.
  """
  result = _query(r'''{
    node(id: "%s") {
      ... on Repository {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 20) {
                nodes {
                  committedDate }}}}}}}}''' % (repo_id))
  history = _getin(result, 'data', 'node', 'defaultBranchRef', 'target', 'history', 'nodes')
  for commit in history:
    yield dateutil.parser.parse(commit['committedDate'])

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
