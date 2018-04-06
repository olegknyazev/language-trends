import asyncio
import os.path

import aiohttp

from language_trends.util import getin

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'

class Session:
  def __init__(self):
    self._aio_session = aiohttp.ClientSession()

  async def __aenter__(self):
    await self._aio_session.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self._aio_session.__aexit__(exc_type, exc_val, exc_tb)

  async def query(self, query):
    """Sends a query to GitHub GraphQL API and returns resulted JSON."""
    # TODO handle errors
    async with self._aio_session.post(
          SERVICE_END_POINT,
          json = {'query': query},
          headers = _auth_headers()
        ) as resp:
      return await resp.json()

async def _process_error(error):
  timeout = _timeout_for(error)
  # TODO use log
  print('Error occured: {}. Waiting for {} seconds...'.format(error, timeout))
  await asyncio.sleep(timeout)

def _timeout_for(error):
  if error == 'ABUSE':
    return 20
  elif error == 'RATE_LIMITED':
    return 10 * 60 # 10 minutes
  elif error == 'UNKNOWN_ERROR':
    return 5
  raise Exception('Unknown error: ' + str(error))

def _analyze_error(result):
  errors = result.get('errors', None)
  if errors:
    error_types = [e.get('type', None) for e in errors]
    if 'RATE_LIMITED' in error_types:
      return 'RATE_LIMITED'
    return 'UNKNOWN_ERROR'
  if 'abuse' in result.get('message', ''):
    return 'ABUSE'
  return None

def _auth_headers():
  token = _auth_token()
  if not token:
    raise Exception(
      f"Authorization token isn't found." +
      f"Be sure that file {AUTH_TOKEN_FILENAME} exists.")
  return {'Authorization': 'bearer ' + token}

_cached_auth_token = None

def _auth_token():
  global _cached_auth_token
  if _cached_auth_token is None:
    if os.path.isfile(AUTH_TOKEN_FILENAME):
      with open(AUTH_TOKEN_FILENAME) as f:
        _cached_auth_token = f.read().strip()
  return _cached_auth_token
