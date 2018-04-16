from . import migrations
from . import access

def main(args):
  def print_usage():
    print('Usage: python -m language_trends.data <command>')
    print('  where <command> is:')
    print('    migrate       - migrate to the latest available version')
    print('    rollback      - rollback the last migration')
    print('    rollback all  - (CAUTION!) rollback to an empty database state')
    print('')
  if not args:
    print_usage()
    return
  cmd = args[0]
  if cmd == 'migrate':
    with access.transaction() as c:
      migrations.migrate(c)
  elif cmd == 'rollback':
    with access.transaction() as c:
      migrations.rollback(c, max_count=(int(args[1]) if len(args) > 1 else -1))
  else:
    print_usage()
    return

if __name__ == '__main__':
  import sys
  main(sys.argv[1:])
