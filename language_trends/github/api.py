import aiohttp
import os.path

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
    async with self._aio_session.post(
          SERVICE_END_POINT,
          json = {'query': query},
          headers = _auth_headers()
        ) as resp:
      return await resp.json()

  async def fetch_paginated(make_query, page_info_path):
    """Fetches content using GraphQL pagination.

      make_query
        Callable producing a query string. Accepts a single argument - cursor,
        which is None during the first call. Resulted query should contain
        a pageInfo node.

      page_info_path
        An Iterable containing path to the node 'pageInfo { endCursor hasNextPage }'.

    More info:
      http://graphql.org/learn/pagination/

    """
    cursor = None
    has_next_page = True
    while has_next_page:
      while True:
        result = await self.query(make_query(cursor))
        if not _is_abuse_report(result):
          break
        print('Abuse detected, sleep') # TODO log?
        await asyncio.sleep(5)
      yield result
      cursor = _getin(result, *page_info_path, 'endCursor')
      has_next_page = _getin(result, *page_info_path, 'hasNextPage')


def _is_abuse_report(result):
  error_message = result.get('message', '')
  return 'abuse' in error_message

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
