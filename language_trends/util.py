from functools import reduce
from itertools import islice, tee
from datetime import datetime

def getin(obj, *path):
  return reduce(lambda obj, seg: obj[seg], path, obj)

def sliding_pairs(iter):
  xs, ys = tee(iter)
  return zip(xs, islice(ys, 1, None))

def current_date():
  return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
