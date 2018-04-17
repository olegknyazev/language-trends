from unittest import TestCase
from datetime import datetime, date

from language_trends.github.queries import _fmt_date

class fmt_date_Test(TestCase):
  def test_returns_a_string_without_microsecond_for_a_datetime(self):
    self.assertEqual('2018-04-02T12:30:17', _fmt_date(datetime(2018, 4, 2, 12, 30, 17, 150)))
    self.assertEqual('2009-11-30T00:02:10', _fmt_date(datetime(2009, 11, 30, 0, 2, 10, 150)))

  def test_returns_a_string_with_zeroed_time_for_a_date(self):
    self.assertEqual('2018-01-17T00:00:00', _fmt_date(date(2018, 1, 17)))
    self.assertEqual('2012-12-01T00:00:00', _fmt_date(date(2012, 12, 1)))

  def test_raises_for_not_a_date_nor_datetime(self):
    with self.assertRaises(Exception):
      _fmt_date('21 Jan. 2001')
