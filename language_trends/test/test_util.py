from unittest import TestCase

from language_trends.util import sliding_pairs

class sliding_pairs_Test(TestCase):
  def test_yields_sliding_pairs(self):
    self.assertListEqual([(1, 2), (2, 3), (3, 4)], list(sliding_pairs([1, 2, 3, 4])))
