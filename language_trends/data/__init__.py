from contextlib import contextmanager
from . import migrations
from . import access

def store(record):
  with _transaction() as c:
    c.execute(
      'INSERT INTO repositories VALUES (%s, %s, %s);',
      (record['id'], record['name'], record['language']))

_migrated = False

@contextmanager
def _transaction():
  if not _migrated:
    with access.transaction() as c:
      migrations.migrate(c)
    _migrated = True
  with access.transaction() as c:
    yield c
