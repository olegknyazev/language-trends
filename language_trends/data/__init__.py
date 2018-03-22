from contextlib import contextmanager
from . import migrations
from . import access

def store_repo(id, name, language):
  with _transaction() as c:
    c.execute(
     '''INSERT INTO repositories VALUES (%s, %s, %s)
          ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                language = EXCLUDED.language;''',
      (id, name, language))

def store_commits(repo_id, date, commits_count):
  with _transaction() as c:
    c.execute(
     '''INSERT INTO commits_per_day VALUES (%s, %s, %s)
          ON CONFLICT (repository_id, date) DO UPDATE
            SET commit_count = EXCLUDED.commit_count;''',
      (repo_id, date, commits_count))

_migrated = False

@contextmanager
def _transaction():
  global _migrated
  if not _migrated:
    with access.transaction() as c:
      migrations.migrate(c)
    _migrated = True
  with access.transaction() as c:
    yield c
