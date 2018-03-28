from unittest import TestCase
from unittest.mock import patch, Mock

from .. import github

class GitHub_Test(TestCase):
  @patch('language_trends.github.requests')
  def test_returns_whatever_server_returns(self, requests):
    requests.post.return_value = Mock()
    requests.post.return_value.json.return_value = {
      'data': {
        'search': {
          'nodes': [
            {'id': 'prj01', 'name': 'Project-01'},
            {'id': 'prj02', 'name': 'Project-02'}
          ],
          'pageInfo': {
            'endCursor': 'abcd23==',
            'hasNextPage': False
          }
        }
      }
    }
    repos = list(github.fetch_repos('C++'))
    requests.post.assert_called()
    self.assertEqual([('prj01', 'Project-01'), ('prj02', 'Project-02')], repos)
