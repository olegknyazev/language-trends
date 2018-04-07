from unittest import TestCase
from datetime import date, datetime

from hypothesis import given
from hypothesis.strategies import tuples, datetimes, lists

from language_trends.util import months, sliding_pairs

_REASONABLE_DATE_RANGE = {
  'min_value': datetime(1995, 1, 1),
  'max_value': datetime(2020, 12, 31)}

def _date_range_tuples():
  return tuples(
      datetimes(**_REASONABLE_DATE_RANGE),
      datetimes(**_REASONABLE_DATE_RANGE)
    ).filter(lambda p: p[0] <= p[1])

class months_Test(TestCase):
  @given(_date_range_tuples())
  def test_yielded_months_should_be_in_provided_range(self, since_until):
    since_month, until_month = [date(d.year, d.month, 1) for d in since_until]
    assert all(m >= since_month and m <= until_month for m in months(*since_until))

  @given(_date_range_tuples())
  def test_yielded_dates_should_be_distinct(self, since_until):
    ms = list(months(*since_until))
    assert len(set(ms)) == len(ms)

  @given(_date_range_tuples())
  def test_yielded_dates_should_be_the_first_day_of_month(self, since_until):
    assert all(getattr(m, 'day', 1) == 1 for m in months(*since_until))

class sliding_pairs_Test(TestCase):
  def test_yields_sliding_pairs(self):
    self.assertListEqual([(1, 2), (2, 3), (3, 4)], list(sliding_pairs([1, 2, 3, 4])))
