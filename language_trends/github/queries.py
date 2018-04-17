import string
import re
from datetime import date, time, datetime
from itertools import starmap

from language_trends.util import sliding_pairs
from language_trends.months import months_between

MAX_PAGE_SIZE = 100

REPO_COUNT_PATH = ['data', 'search', 'repositoryCount']
def repo_count(lang, **search_args):
  return string.Template(r'''{
      $search {
        repositoryCount
      }}''').substitute(search=_search_clause(lang, **search_args))

SEARCH_REPOS_BASE_PATH = ['data', 'search', 'nodes']
def search_repos(lang, repository_fields, **search_args):
  return string.Template(r'''{
      $search {
        nodes {
          ... on Repository {
            $repository_fields }}}}''').substitute(
              search=_search_clause(lang, **search_args),
              repository_fields=' '.join(repository_fields))

REPO_MONTHLY_TOTAL_COMMITS_BASE_PATH = ['data', 'node', 'defaultBranchRef', 'target']
def repo_monthly_total_commits(repo_id, since, until):
  return string.Template(r'''{
      node(id: "$repo_id") {
        ... on Repository {
          defaultBranchRef {
            target {
              ... on Commit {
                $history }}}}}}''').substitute(
                  repo_id=repo_id,
                  history=_history_clauses(since, until))

_ID_TO_MONTH_PATTERN = re.compile(r'_(\d{4})_(\d{1,2})')

def month_id_to_date(month_id):
  match = _ID_TO_MONTH_PATTERN.fullmatch(month_id)
  return date(int(match.group(1)), int(match.group(2)), 1)

def _history_clauses(since, until):
  return '\n'.join(starmap(_commits_within, sliding_pairs(months_between(since, until))))

def _commits_within(since, until):
  month_id = f'_{until.year}_{until.month}'
  history_args = f'since: "{_fmt_date(since)}", until: "{_fmt_date(until)}"'
  return f'{month_id}: history({history_args}) {{ totalCount }}'

def _search_clause(lang, *, first=MAX_PAGE_SIZE, created_range=None, pushed_after=None):
  args = {'first': first}
  args.update(_search_args(lang, created_range=created_range, pushed_after=pushed_after))
  return f'search ({_join_args(args)})'

def _search_args(lang, *, created_range=None, pushed_after=None):
  additional_args = ''
  if created_range is not None:
    additional_args += f' created:{_fmt_date(created_range[0])}..{_fmt_date(created_range[1])}'
  if pushed_after is not None:
    additional_args += f' pushed:>={_fmt_date(pushed_after)}'
  return {
    'query': f'"language:{lang} size:>=10000 {additional_args}"',
    'type': 'REPOSITORY'}

def _join_args(args):
  return ', '.join(f'{k}: {v}' for k, v in args.items())

def _fmt_date(d):
  if isinstance(d, datetime):
    return d.replace(microsecond=0).isoformat()
  if isinstance(d, date):
    return datetime.combine(d, time.min).isoformat()
  raise Exception(f'{d} is not a date nor datetime')

