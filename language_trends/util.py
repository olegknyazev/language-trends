from functools import reduce
from itertools import islice, tee

def getin(obj, *path):
  return reduce(lambda obj, seg: obj[seg], path, obj)

def sliding_pairs(iter):
  xs, ys = tee(iter)
  return zip(xs, islice(ys, 1, None))
