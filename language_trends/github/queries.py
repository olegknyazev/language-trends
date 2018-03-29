import string
from datetime import datetime

PAGE_SIZE = 100

def pagination_params(first=None, after=None):
  result = {}
  if first is not None: result['first'] = first
  if after is not None: result['after'] = f'"{after}"'
  return result

def search_params(language):
  return {
    'query': f'"language:{language} size:>=10000"',
    'type': 'REPOSITORY'}

def join_params(**params): return ', '.join(f'{k}: {v}' for k, v in params.items())

def search_clause(language, first=None, after=None):
  params = {}
  params.update(search_params(language))
  params.update(pagination_params(first, after))
  return f'search ({join_params(**params)})'

def format_repos_query(language, cursor=None):
  return string.Template(r'''{
      $search {
        nodes {
          ... on Repository {
            id
            name }}
        pageInfo {
          endCursor
          hasNextPage }}}''').substitute(
            search=search_clause(language, first=PAGE_SIZE, after=cursor))

def format_commits_query(repo_id, since=None, cursor=None):
  history_args = {}
  if since is not None:
    if isinstance(since, datetime):
      since = since.isoformat()
    history_args['since'] = f'"{since}"'
  history_args.update(pagination_params(first=PAGE_SIZE, after=cursor))
  return string.Template(r'''{
      node(id: "$id") {
        ... on Repository {
          defaultBranchRef {
            target {
              ... on Commit {
                history($history_args) {
                  nodes {
                    committedDate }
                  pageInfo {
                    endCursor
                    hasNextPage }}}}}}}}''').substitute(
                      id=repo_id,
                      history_args=join_params(**history_args))
