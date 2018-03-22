import requests
import os.path

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'

def fetch_repos(language):
  result = _query('''{
      search(query: "language:%s", type: REPOSITORY, first: 20) {
        edges {
          node {
            ... on Repository {
              id
              name
            }
          }
          cursor
        }
      }
  }''' % (language))
  edges = result['data']['search']['edges']
  for e in edges:
    yield e['node']['id'], e['node']['name']

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
