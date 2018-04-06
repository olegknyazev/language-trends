from datetime import datetime

from language_trends.util import getin
from . import queries
from . import api

BEGIN_OF_TIME = datetime(2008, 1, 1)
END_OF_TIME = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

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

  async def fetch_commits_monthly_breakdown(self, repo_id, since=BEGIN_OF_TIME, until=END_OF_TIME):
    def iterate_commits(monthly_commits):
      previous_count = 0
      for date, info in monthly_commits:
        total_count = info['totalCount']
        delta = total_count - previous_count
        previous_count = total_count
        yield date, delta, total_count

    result = (
      await self._api_session.query(
        queries.repo_monthly_total_commits(repo_id, since, until)))
    monthly_commits = getin(result, *queries.REPO_MONTHLY_TOTAL_COMMITS_BASE_PATH)
    monthly_commits = [(queries.month_id_to_date(d), info) for d, info in monthly_commits.items()]
    monthly_commits.sort(key=lambda kv: kv[0])
    return iterate_commits(monthly_commits)

  async def fetch_repos(self, language, fields, since=None):
    async def fetch(selector, start, end):
      result = (
        await self._api_session.query(
          queries.search_repos(language, fields, **{selector: (start, end)})))
      for repo in getin(result, *queries.SEARCH_REPOS_BASE_PATH):
        yield repo

    async def binary_traverse(selector, start, end, offset=0):
      count = await self.repo_count(language, **{selector: (start, end)})
      if count < queries.MAX_PAGE_SIZE:
        async for repo in fetch(selector, start, end):
          yield repo
      else:
        mid = start + (end - start) / 2
        async for repo in binary_traverse(selector, start, mid, offset + 1):
          yield repo
        async for repo in binary_traverse(selector, mid, end, offset + 1):
          yield repo

    if since is None:
      generator = binary_traverse('created_range', BEGIN_OF_TIME, END_OF_TIME)
    else:
      generator = binary_traverse('pushed_range', since, END_OF_TIME)
    async for repo in generator:
      yield repo

