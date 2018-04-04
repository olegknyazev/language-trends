import functools

def getin(obj, *path):
  return functools.reduce(lambda obj, seg: obj[seg], path, obj)
