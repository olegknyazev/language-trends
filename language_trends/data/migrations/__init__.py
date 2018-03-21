import itertools
import os
import re
from glob import glob

def migrate(cursor):
  _initialize_migration_table(cursor)
  cursor.execute('SELECT * FROM migrations ORDER BY name;')
  start_idx = 0
  applied_migrations = [m[0] for m in cursor]
  all_migrations = _available_migrations()
  if applied_migrations:
    last_migration = applied_migrations[-1]
    start_idx = all_migrations.index(last_migration) + 1
  _perform_migrations(cursor, itertools.islice(all_migrations, start_idx, len(all_migrations)))

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

def _initialize_migration_table(cursor):
  cursor.execute('CREATE TABLE IF NOT EXISTS migrations (name varchar(40) PRIMARY KEY);')

def _perform_migrations(cursor, migrations):
  import importlib
  for m in migrations:
    mig_module = importlib.import_module('.' + m, __package__)
    mig_module.perform(cursor)
    cursor.execute('INSERT INTO migrations VALUES (%s)', (m,))
