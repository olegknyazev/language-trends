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
     '''INSERT INTO commits_by_repo VALUES (%s, %s, %s)
          ON CONFLICT (repository_id, date) DO UPDATE
            SET commit_count = EXCLUDED.commit_count;''',
      (repo_id, date, commits_count))

def store_commits(repo_id, data):
  with _transaction() as c:
    access.execute_values(c,
     '''INSERT INTO commits_by_repo VALUES %s
          ON CONFLICT (repository_id, date) DO UPDATE
            SET commit_count = EXCLUDED.commit_count;''',
      ((repo_id, date, commits) for date, commits in data))

def update_aggregated_data():
  with _transaction() as c:
    c.execute('''
      REFRESH MATERIALIZED VIEW commit_by_language;
      REFRESH MATERIALIZED VIEW commit_by_language_monthly;''')

def repo_count(language):
  with _transaction() as c:
    c.execute('SELECT COUNT(*) FROM repositories WHERE language = %s;', (language,))
    return c.fetchone()[0]

def last_commit_date(repo_id):
  with _transaction() as c:
    c.execute('SELECT MAX(date) FROM commits_by_repo WHERE repository_id = %s', (repo_id,))
    return c.fetchone()[0]

def commits_by_language(language):
  with _transaction() as c:
    c.execute(
     '''SELECT c.date, SUM(c.commit_count)
          FROM commits_by_repo c JOIN repositories r ON c.repository_id = r.id
          WHERE r.language = %s
          GROUP BY c.date
          ORDER BY c.date;''',
      (language,))
    return list(c)

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
