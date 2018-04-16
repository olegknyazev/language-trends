from contextlib import contextmanager

from . import migrations
from . import access

def store_repo(id, name, language):
  with _transaction() as c:
    c.execute('''
      INSERT INTO repos VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE
          SET name = EXCLUDED.name,
              lang = EXCLUDED.lang;''',
      (id, name, language))

def store_commits(repo_id, data):
  with _transaction() as c:
    access.execute_values(c,
     '''INSERT INTO commits VALUES %s
          ON CONFLICT (repo_id, date) DO UPDATE
            SET commits_since_prev = EXCLUDED.commits_since_prev,
                commits_total = EXCLUDED.commits_total;''',
      ((repo_id, *cols) for cols in data))

def store_lang_scan(lang, actual_by):
  with _transaction() as c:
    c.execute('''
      INSERT INTO lang_scans VALUES (%s, %s)
        ON CONFLICT (lang) DO UPDATE
          SET actual_by = EXCLUDED.actual_by;''',
      (lang, actual_by))

def update_aggregated_data():
  with _transaction() as c:
    c.execute('REFRESH MATERIALIZED VIEW commits_by_lang;')

def repo_count(language):
  with _transaction() as c:
    c.execute('SELECT COUNT(*) FROM repos WHERE lang = %s;', (language,))
    return c.fetchone()[0]

def is_repo_exists(repo_id):
  with _transaction() as c:
    c.execute('SELECT COUNT(*) FROM repos WHERE id = %s;', (repo_id,))
    return c.fetchone()[0] == 1

def lang_actual_by(lang):
  with _transaction() as c:
    c.execute('SELECT actual_by FROM lang_scans WHERE lang = %s;', (lang,))
    row = c.fetchone()
    return row[0] if row else None

def language_stats(languages):
  """Returns a list containing (lang, repo_count, commit_count) for each lang from
  the passed languages Iterable.
  """
  report = []
  with _transaction() as c:
    for lang in languages:
      c.execute('SELECT DISTINCT COUNT(*) FROM repos WHERE lang = %s;', (lang,))
      repo_count = c.fetchone()[0] or 0
      c.execute('''
        SELECT SUM(c.commits_since_prev)
          FROM commits c JOIN repos r ON c.repo_id = r.id
          WHERE r.lang = %s;
        ''', (lang,))
      commit_count = c.fetchone()[0] or 0
      report.append((lang, repo_count, commit_count))
    return report

def commits_by_language(language):
  with _transaction() as c:
    c.execute(f'''
      SELECT date, commits_since_prev
        FROM commits_by_lang
        WHERE lang = %s
        ORDER BY date;''',
      (language,))
    return [(x[0], int(x[1])) for x in c]

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
