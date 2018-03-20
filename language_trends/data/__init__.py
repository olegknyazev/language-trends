import psycopg2 as db
from contextlib import contextmanager
import os.path
from glob import glob
import itertools

CONNECTION_PARAMS = {
  'host': 'localhost',
  'dbname': 'language-trends',
  'user': 'language-trends',
  'password': 'language-trends'
}

_conn = None

def is_initialized(): return _conn is not None

def initialize():
  global _conn
  if is_initialized():
    return
  _conn = db.connect(**CONNECTION_PARAMS)
  with _cursor() as c:
    _initialize_migration_table(c)
    _migrate(c)

def store(record):
  if not is_initialized():
    initialize()
  with _cursor() as c:
    c.execute(
      'INSERT INTO repositories VALUES (%s, %s, %s);',
      (record['id'], record['name'], record['language']))

def _initialize_migration_table(c):
  c.execute('CREATE TABLE IF NOT EXISTS migrations (name varchar(40) NOT NULL);')

_avail_migrations = None
def _available_migrations():
  global _avail_migrations
  if _avail_migrations is None:
    _avail_migrations = glob(os.path.join(os.path.dirname(__file__), 'migrations', '*.py'))
    _avail_migrations.sort()
  return _avail_migrations

def _migrate(c):
  c.execute('SELECT * FROM migrations ORDER BY name;')
  start_idx = 0
  applied_migrations = [m[0] for m in c]
  all_migrations = _available_migrations()
  if applied_migrations:
    last_migration = applied_migrations[-1]
    start_idx = all_migrations.index(last_migration)
  _perform_migrations(c, itertools.islice(all_migrations, start_idx, len(all_migrations)))

def _perform_migrations(c, migrations):
  for m in migrations:
    print(f'APPLYING {m}')

@contextmanager
def _cursor():
  c = _conn.cursor()
  try:
    yield c
    _conn.commit()
  finally:
    c.close()
