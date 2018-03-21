import sys
from language_trends import data

def migrate():
  with data.transaction() as c:
    data.migrations.migrate(c)

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print('Expected exactly one argument')
    exit()
  cmd = sys.argv[1]
  func = globals().get(cmd, None)
  if func is None:
    print('Unknown command: ' + cmd)
    exit()
  func()
