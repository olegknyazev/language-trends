import psycopg2 as db
from contextlib import contextmanager

CONNECTION_PARAMS = {
  'host': 'localhost',
  'dbname': 'language-trends',
  'user': 'language-trends',
  'password': 'language-trends'
}

_conn = None

def is_initialized():
  global _conn
  return _conn is not None

def initialize():
  global _conn
  if is_initialized():
    return
  _conn = db.connect(**CONNECTION_PARAMS)
  _initialize_schema()

def store(record):
  if not is_initialized():
    initialize()
  with _cursor() as c:
    c.execute(
      'INSERT INTO repositories VALUES (%s, %s, %s)',
      (record['id'], record['name'], record['language']))

def _initialize_schema():
  with _cursor() as c:
    c.execute(
  '''CREATE TABLE IF NOT EXISTS repositories (
        id varchar(40) PRIMARY KEY,
        name varchar(40) NOT NULL,
        language varchar(40) NOT NULL)''')

@contextmanager
def _cursor():
  c = _conn.cursor()
  try:
    yield c
    _conn.commit()
  finally:
    c.close()
