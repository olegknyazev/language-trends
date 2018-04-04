import dateutil.parser

from language_trends.collutil import getin
from . import queries
from . import api

class Session:
  def __init__(self):
    self._api_session = api.Session()

  async def __aenter__(self):
    await self._api_session.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self._api_session.__aexit__(exc_type, exc_val, exc_tb)

  async def repo_count(self, language):
    """Returns number of repositories by the specified language."""
    result = await self._api_session.query(queries.repo_count(language))
    return getin(result, *queries.REPO_COUNT_PATH)

  async def fetch_repos(self, language):
    """Yields all the repositories in the form (id, name) for the specified language."""
    pages = self._api_session.fetch_paginated(
      lambda c: queries.repos(language, ['id', 'name'], cursor=c),
      [*queries.REPOS_BASE_PATH, 'pageInfo'])
    async for page in pages:
      for node in getin(page, *queries.REPOS_BASE_PATH, 'nodes'):
        yield node['id'], node['name']

  async def fetch_commits(self, repo_id, since=None):
    """Yields all the commits from the repository specified by repo_id, starting
    from the most recent one.
    """
    pages = self._api_session.fetch_paginated(
      lambda c: queries.commits(repo_id, ['committedDate'], since=since, cursor=c),
      [*queries.COMMITS_BASE_PATH, 'pageInfo'])
    async for page in pages:
      for commit in getin(page, *queries.COMMITS_BASE_PATH, 'nodes'):
        yield dateutil.parser.parse(commit['committedDate'])
