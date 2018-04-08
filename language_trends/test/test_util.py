from unittest import TestCase
from datetime import date, datetime

from hypothesis import given, reproduce_failure
from hypothesis.strategies import tuples, datetimes, lists

from language_trends.util import *

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

  def test_add_months_returns_new_date(self):
    self.assertEqual(date(2018, 8, 1), add_months(date(2018, 4, 1), 4))
    self.assertEqual(date(2018, 5, 1), add_months(date(2017, 2, 1), 15))

  def test_month_between_returns_count_of_months(self):
    self.assertEqual(6, months_between(date(2000, 2, 1), date(2000, 7, 1)))
    self.assertEqual(9, months_between(date(2007, 9, 1), date(2008, 5, 1)))

  @given(_date_range_tuples())
  def test_months_between_returns_the_same_count_as_months(self, since_until):
    assert months_between(*since_until) == sum(1 for x in months(*since_until))

class sliding_pairs_Test(TestCase):
  def test_yields_sliding_pairs(self):
    self.assertListEqual([(1, 2), (2, 3), (3, 4)], list(sliding_pairs([1, 2, 3, 4])))
