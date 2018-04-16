from datetime import datetime, timezone

import dateutil.parser

from language_trends.util import getin, current_date
from language_trends.months import num_of_months_between, add_months, first_day_of_month
from . import queries
from . import api

BEGIN_OF_TIME = datetime(2008, 1, 1)

# TODO transform into bunch of free functions? (client will create an underlying session directly)
class Session:
  def __init__(self):
    self._api_session = api.Session()

  @property
  def abuse_detected(self): return self._api_session.abuse_detected

  @property
  def rate_limited(self): return self._api_session.rate_limited

  @property
  def requests_sent(self): return self._api_session.requests_sent

  async def __aenter__(self):
    await self._api_session.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self._api_session.__aexit__(exc_type, exc_val, exc_tb)

  async def repo_count(self, language, **query_args):
    """Returns number of repositories by the specified language."""
    result = await self._api_session.query(queries.repo_count(language, **query_args))
    return getin(result, *queries.REPO_COUNT_PATH)

  async def fetch_commits_monthly_breakdown(self, repo_id, since=BEGIN_OF_TIME, until=None):
    def iterate_commits(monthly_commits):
      total_count = 0
      for date, info in monthly_commits:
        monthly_count = info['totalCount']
        total_count += monthly_count
        yield date, monthly_count, total_count

    since = first_day_of_month(since)
    until = first_day_of_month(until or current_date())

    num_intervals = num_of_months_between(since, until) - 1
    monthly_commits = []
    interval_width = 40
    while len(monthly_commits) < num_intervals:
      interval = len(monthly_commits)
      curr_since = add_months(since, interval)
      curr_until = min(*(until, add_months(since, interval + interval_width)))
      try:
        result = (
          await self._api_session.query(
            queries.repo_monthly_total_commits(repo_id, curr_since, curr_until)))
      except api.AnswerError:
        if interval_width > 5:
          interval_width //= 2
          continue
        else:
          raise
      commits = getin(result, *queries.REPO_MONTHLY_TOTAL_COMMITS_BASE_PATH)
      commits = [(queries.month_id_to_date(d), info) for d, info in commits.items()]
      monthly_commits += commits

    monthly_commits.sort(key=lambda kv: kv[0])
    return iterate_commits(monthly_commits)

  async def fetch_repos(self, language, fields, pushed_since=None, until=None):
    async def fetch(selector, start, end):
      result = (
        await self._api_session.query(
          queries.search_repos(language, fields, **{selector: (start, end)})))
      for repo in getin(result, *queries.SEARCH_REPOS_BASE_PATH):
        yield _parse_dates_to_utc(repo)

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

    until = until or current_date()

    if pushed_since is None:
      generator = binary_traverse('created_range', BEGIN_OF_TIME, until)
    else:
      generator = binary_traverse('pushed_range', pushed_since, until)

    async for repo in generator:
      yield repo

_DATE_KEYS = ['createdAt', 'pushedAt']

def _parse_date_to_utc(date_str):
  return dateutil.parser.parse(date_str).astimezone(timezone.utc).replace(tzinfo=None)

def _parse_dates_to_utc(dict):
  return {k: _parse_date_to_utc(v) if k in _DATE_KEYS else v for k, v in dict.items()}
