from datetime import datetime

from dateutil.parser import parse as parse_date

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

  async def repo_count(self, language, **query_args):
    """Returns number of repositories by the specified language."""
    result = await self._api_session.query(queries.repo_count(language, **query_args))
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

  async def fetch_repo_commits(self, language, since=None):
    fetched = 0

    def parse_commits(repo):
      nodes = getin(repo, *queries.REPOS_WITH_COMMITS_COMMITS_PATH)
      return (parse_date(commit['committedDate']) for commit in nodes)

    async def fetch(selector, start, end):
      result = await self._api_session.query(
        queries.repos_with_commits(
          language,
          ['id', 'name'],
          ['committedDate'],
          **{selector: (start, end)}))
      repos = getin(result, *queries.REPOS_WITH_COMMITS_REPO_PATH)
      for repo in repos:
        yield repo['id'], repo['name'], parse_commits(repo)

    async def impl(selector, start, end, offset=0):
      nonlocal fetched
      pad = ' ' * offset
      count = await self.repo_count(language, **{selector: (start, end)})
      print(pad + f'QUERY {selector}: {start}..{end} --> {count}')
      if count < 100:
        fetched += count
        async for repo in fetch(selector, start, end):
          yield repo
      else:
        mid = start + (end - start) / 2
        async for repo in impl(selector, start, mid, offset + 1):
          yield repo
        async for repo in impl(selector, mid, end, offset + 1):
          yield repo

    if since is None:
      generator = impl('created_range', _BEGIN_OF_TIME, _END_OF_TIME)
    else:
      generator = impl('pushed_range', since, _END_OF_TIME)

    async for repo in generator:
      yield repo

    print(f'FETCHED {fetched}')

_BEGIN_OF_TIME = datetime(2008, 1, 1)
_END_OF_TIME = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
