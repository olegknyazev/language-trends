from unittest import TestCase
from unittest.mock import patch, Mock

from .. import github

class github_Test(TestCase):
  @patch('language_trends.github.requests')
  def test_returns_whatever_server_returns(self, requests):
    repos = [('prj01', 'Project-01'), ('prj02', 'Project-02')]
    requests.post.return_value = Mock()
    requests.post.return_value.json.return_value = self._repo_page(repos)
    returned_repos = list(github.fetch_repos('C++'))
    self.assertEqual(repos, returned_repos)

  @patch('language_trends.github.requests')
  def test_asks_following_pages_if_there_is_any(self, requests):
    repos = [
      ('clj01', 'ring'), ('clj02', 'leiningen'),
      ('clj03', 'datomic'), ('clj04', 'korma'),
      ('clj05', 'LightTable'), ('clj06', 'compojure')
    ]
    requests.post.return_value = Mock()
    requests.post.return_value.json.side_effect = [
      self._repo_page(repos[0:2], end_cursor='c1', has_next_page=True),
      self._repo_page(repos[2:4], end_cursor='c2', has_next_page=True),
      self._repo_page(repos[4:], has_next_page=False)
    ]
    returned_repos = list(github.fetch_repos('clojure'))
    self.assertEqual(repos, returned_repos)
    self.assertNotIn('after:', requests.post.call_args_list[0][1]['json']['query'])
    self.assertIn('after: "c1"', requests.post.call_args_list[1][1]['json']['query'])
    self.assertIn('after: "c2"', requests.post.call_args_list[2][1]['json']['query'])

  def _repo_page(self, repos, end_cursor='', has_next_page=False):
    return {
      'data': {
        'search': {
          'nodes': [{'id': r[0], 'name': r[1]} for r in repos],
          'pageInfo': {
            'endCursor': end_cursor,
            'hasNextPage': has_next_page }}}}
