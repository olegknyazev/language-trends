import string

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
