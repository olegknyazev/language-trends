import requests
import os.path

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'

_cached_auth_token = None
def auth_token():
  global _cached_auth_token
  if _cached_auth_token is None:
    if os.path.isfile(AUTH_TOKEN_FILENAME):
      with open(AUTH_TOKEN_FILENAME) as f:
        _cached_auth_token = f.read().strip()
  return _cached_auth_token

def auth_headers():
  token = auth_token()
  if not token:
    raise Exception(
      f"Authorization token isn't found." +
      f"Be sure that file {AUTH_TOKEN_FILENAME} exists.")
  return {'Authorization': 'bearer ' + token}

EXAMPLE_REQ = '''{
  search(query: "language:JavaScript, stars:>10000", type: REPOSITORY, first: 10) {
    repositoryCount
    edges {
      node {
        ... on Repository {
          name
          stargazers {
            totalCount
          }
        }
      }
    }
  }
}'''

def example_search():
  return requests.post(
    SERVICE_END_POINT,
    json={'query': EXAMPLE_REQ},
    headers=auth_headers()).json()
