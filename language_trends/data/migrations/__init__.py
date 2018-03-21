import itertools
import os
import re
from glob import glob

def migrate(cursor):
  _initialize_migration_table(cursor)
  applied_migrations = _query_applied_migrations(cursor)
  start_idx = 0
  all_migrations = _available_migrations()
  if applied_migrations:
    last_migration = applied_migrations[-1]
    start_idx = all_migrations.index(last_migration) + 1
  _perform_migrations(cursor, itertools.islice(all_migrations, start_idx, len(all_migrations)))

def rollback(cursor):
  _initialize_migration_table(cursor)
  _rollback_migrations(cursor, _query_applied_migrations(cursor))

MIGRATION_PATTERN = re.compile(r'_\d{3}_.*\.py')

def _migrations_path(): return os.path.dirname(__file__)

def _query_applied_migrations(cursor):
  cursor.execute('SELECT * FROM migrations ORDER BY name;')
  return [m[0] for m in cursor]

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

def _migration_modules(migrations):
  import importlib
  for name in migrations:
    module = importlib.import_module('.' + name, __package__)
    yield name, module

def _perform_migrations(cursor, migrations):
  for name, module in _migration_modules(migrations):
    module.perform(cursor)
    cursor.execute('INSERT INTO migrations VALUES (%s);', (name,))

def _rollback_migrations(cursor, migrations):
  for name, module in _migration_modules(reversed(migrations)):
    module.rollback(cursor)
    cursor.execute('DELETE FROM migrations WHERE name = %s;', (name,))
