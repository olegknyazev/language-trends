import itertools
import os
import re
from glob import glob

def migrate(cursor):
  _initialize_migration_table(cursor)
  applied_migs = _query_applied_migrations(cursor)
  all_migs = _load_available_migrations()
  start_idx = all_migs.index(applied_migs[-1]) + 1 if applied_migs else 0
  _perform_migrations(cursor, itertools.islice(all_migs, start_idx, len(all_migs)))

def rollback(cursor):
  _initialize_migration_table(cursor)
  _rollback_migrations(cursor, _query_applied_migrations(cursor))

MIGRATION_PATTERN = re.compile(r'_\d{3}_.*\.py')

def _migrations_path(): return os.path.dirname(__file__)

def _query_applied_migrations(cursor):
  cursor.execute('SELECT * FROM migrations ORDER BY name;')
  return [m[0] for m in cursor]

def _load_available_migrations():
  return sorted(
    os.path.splitext(f)[0] for f in os.listdir(_migrations_path())
      if MIGRATION_PATTERN.fullmatch(f))

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
