import itertools
import os
import re
from glob import glob

def migrate(c):
  _initialize_migration_table(c)
  c.execute('SELECT * FROM migrations ORDER BY name;')
  start_idx = 0
  applied_migrations = [m[0] for m in c]
  all_migrations = _available_migrations()
  if applied_migrations:
    last_migration = applied_migrations[-1]
    start_idx = all_migrations.index(last_migration)
  _perform_migrations(c, itertools.islice(all_migrations, start_idx, len(all_migrations)))

def _migrations_path(): return os.path.dirname(__file__)

MIGRATION_PATTERN = re.compile(r'_\d{3}_.*\.py')

_avail_migrations = None
def _available_migrations():
  global _avail_migrations
  if _avail_migrations is None:
    _avail_migrations = [
      os.path.splitext(f)[0] for f in os.listdir(_migrations_path())
        if MIGRATION_PATTERN.fullmatch(f)]
    _avail_migrations.sort()
  return _avail_migrations

def _initialize_migration_table(c):
  c.execute('CREATE TABLE IF NOT EXISTS migrations (name varchar(40) NOT NULL);')

def _perform_migrations(c, migrations):
  for m in migrations:
    print(f'APPLYING {m}')
