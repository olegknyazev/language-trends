import sys
import language_trends.data.access as data_access
import language_trends.data.migrations as migrations

def migrate(max_count = -1):
  with data_access.transaction() as c:
    migrations.migrate(c, int(max_count))

def rollback(max_count = -1):
  with data_access.transaction() as c:
    migrations.rollback(c, int(max_count))

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('At least one argument expected')
    exit()
  cmd = sys.argv[1]
  func = globals().get(cmd, None)
  if func is None:
    print('Unknown command: ' + cmd)
    exit()
  func(*sys.argv[2:])
