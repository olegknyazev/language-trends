import sys
import language_trends.data.access as data_access
import language_trends.data.migrations as migrations

def migrate():
  with data_access.transaction() as c:
    migrations.migrate(c)

def rollback():
  with data_access.transaction() as c:
    migrations.rollback(c)

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
