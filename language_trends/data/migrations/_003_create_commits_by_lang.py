def perform(cursor):
  cursor.execute('''
    CREATE MATERIALIZED VIEW commits_by_lang AS
      SELECT
          r.lang,
          c.date,
          SUM(c.commits_since_prev) AS commits_since_prev,
          SUM(c.commits_total) AS commits_total
        FROM commits c INNER JOIN repos r ON c.repo_id = r.id
        GROUP BY r.lang, c.date;
  ''')

def rollback(cursor):
  cursor.execute('DROP MATERIALIZED VIEW commits_by_lang;')
