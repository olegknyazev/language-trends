from contextlib import contextmanager

import psycopg2 as db
import psycopg2.extras

CONNECTION_PARAMS = {
  'host': 'localhost',
  'dbname': 'language-trends',
  'user': 'language-trends',
  'password': 'language-trends'
}

execute_values = psycopg2.extras.execute_values

@contextmanager
def transaction():
  if not _is_initialized():
    _initialize()
  cursor = _conn.cursor()
  try:
    yield cursor
    _conn.commit()
  except:
    _conn.rollback()
    raise
  finally:
    cursor.close()

_conn = None

def _is_initialized(): return _conn is not None

def _initialize():
  global _conn
  assert _conn is None
  _conn = db.connect(**CONNECTION_PARAMS)
