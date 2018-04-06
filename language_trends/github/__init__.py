from datetime import datetime

from dateutil.parser import parse as parse_date

from language_trends.util import getin
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

  async def fetch_repos_with_commits(self, language, since=None):
    fetched = 0

    def iterate_commits(monthly_commits):
      previous_count = 0
      for date, info in sorted(monthly_commits.items(), key=lambda kv: kv[0]):
        total_count = info['totalCount']
        delta = total_count - previous_count
        previous_count = total_count
        yield date, delta, total_count

    async def fetch_commits(repo_id, start, end):
      result = await self._api_session.query(
        queries.repo_monthly_total_commits(repo_id, start, end))
      monthly_commits = getin(result, *queries.REPO_MONTHLY_TOTAL_COMMITS_BASE_PATH)
      return iterate_commits(monthly_commits)

    async def fetch_repos(selector, start, end):
      result = await self._api_session.query(
        queries.search_repos(
          language,
          ['id', 'name', 'createdAt', 'pushedAt'],
          **{selector: (start, end)}))
      repos = getin(result, *queries.SEARCH_REPOS_BASE_PATH)
      for repo in repos:
        repo_id = repo['id']
        created_at = parse_date(repo['createdAt'])
        pushed_at = parse_date(repo['pushedAt'])
        commits = await fetch_commits(repo_id, created_at, pushed_at)
        yield repo_id, repo['name'], commits

    async def impl(selector, start, end, offset=0):
      nonlocal fetched
      pad = ' ' * offset
      count = await self.repo_count(language, **{selector: (start, end)})
      print(pad + f'QUERY {selector}: {start}..{end} --> {count}')
      if count < 100:
        fetched += count
        async for repo in fetch_repos(selector, start, end):
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
