import asyncio
import os.path

import aiohttp

from language_trends.util import getin

AUTH_TOKEN_FILENAME = './auth_token.txt'
SERVICE_END_POINT = 'https://api.github.com/graphql'

class Session:
  def __init__(self):
    self._aio_session = aiohttp.ClientSession()
    self.requests_sent = 0
    self.abuse_detected = False
    self.rate_limited = False

  async def __aenter__(self):
    await self._aio_session.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self._aio_session.__aexit__(exc_type, exc_val, exc_tb)

  async def query(self, query):
    """Sends a query to GitHub GraphQL API and returns resulted JSON."""
    while True:
      self.requests_sent += 1
      async with self._aio_session.post(
            SERVICE_END_POINT,
            json = {'query': query},
            headers = _auth_headers()
          ) as resp:
        self.abuse_detected = False
        self.rate_limited = False
        answer = await resp.json()
        if _is_abuse(answer):
          self.abuse_detected = True
          await asyncio.sleep(20)
          continue
        if _is_rate_limited(answer):
          self.rate_limited = True
          await asyncio.sleep(60 * 10)
          continue
        if _is_error(answer):
          raise AnswerError(answer)
        return answer

class AnswerError(Exception):
  def __init__(self, answer):
    super().__init__(_errors_string(answer))
    self.answer = answer

def _is_abuse(answer):
  return 'abuse' in answer.get('message', '')

def _is_rate_limited(answer):
  return any('RATE_LIMITED' in e.get('type', '') for e in answer.get('errors', []))

def _is_error(answer):
  return 'errors' in answer

def _errors_string(answer):
  return '\n'.join(e.get('message', '') for e in answer.get('errors', []))

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
