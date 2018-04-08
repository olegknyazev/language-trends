from functools import reduce
from itertools import islice, tee, count, starmap
from datetime import date
import operator

def getin(obj, *path):
  return reduce(lambda obj, seg: obj[seg], path, obj)

def months_starting_from(since):
  year = since.year
  month = since.month
  while True:
    yield date(year, month, 1)
    month += 1
    if month > 12:
      month = 1
      year += 1

def months(since, until):
  for d in months_starting_from(since):
    yield d
    if d.year >= until.year and d.month >= until.month:
      break

def sliding_pairs(iter):
  xs, ys = tee(iter)
  return zip(xs, islice(ys, 1, None))

def add_months(d, months):
  new_months = d.month + months - 1
  return date(d.year + new_months // 12, new_months % 12 + 1, d.day)

def months_between(since, until):
  return (until.year - since.year) * 12 + (until.month - since.month) + 1
