import psycopg2 as db
from contextlib import contextmanager
from .migrations import migrate

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
    migrate(c)

def store(record):
  if not is_initialized():
    initialize()
  with _cursor() as c:
    c.execute(
      'INSERT INTO repositories VALUES (%s, %s, %s);',
      (record['id'], record['name'], record['language']))

@contextmanager
def _cursor():
  cursor = _conn.cursor()
  try:
    yield cursor
    _conn.commit()
  finally:
    cursor.close()
