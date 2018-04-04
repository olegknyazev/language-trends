import functools
import dateutil.parser

from . import queries
from . import api

async def repo_count(language):
  """Returns number of repositories by the specified language."""
  async with api.Session() as session:
    result = await session.query(queries.repo_count(language))
    return _getin(result, *queries.REPO_COUNT_PATH)

async def fetch_repos(language):
  """Yields all the repositories in the form (id, name) for the specified language."""
  async with api.Session() as session:
    pages = session.fetch_paginated(
      lambda c: queries.repos(language, ['id', 'name'], cursor=c),
      [*queries.REPOS_BASE_PATH, 'pageInfo'])
    async for page in pages:
      for node in _getin(page, *queries.REPOS_BASE_PATH, 'nodes'):
        yield node['id'], node['name']

async def fetch_commits(repo_id, since=None):
  """Yields all the commits from the repository specified by repo_id, starting
  from the most recent one.
  """
  async with api.Session() as session:
    pages = session.fetch_paginated(
      lambda c: queries.commits(repo_id, ['committedDate'], since=since, cursor=c),
      [*queries.COMMITS_BASE_PATH, 'pageInfo'])
    async for page in pages:
      for commit in _getin(page, *queries.COMMITS_BASE_PATH, 'nodes'):
        yield dateutil.parser.parse(commit['committedDate'])

def _getin(obj, *path):
  return functools.reduce(lambda obj, seg: obj[seg], path, obj)
