def perform(cursor):
  cursor.execute('''
    CREATE MATERIALIZED VIEW commit_by_language AS
      SELECT r.language, c.date, SUM(c.commit_count) AS commit_count
        FROM commits_by_repo c INNER JOIN repositories r ON c.repository_id = r.id
        GROUP BY r.language, c.date;

    CREATE MATERIALIZED VIEW commit_by_language_monthly AS
      SELECT
          language,
          date_trunc('month', date) AS date,
          SUM(commit_count) AS commit_count
        FROM commit_by_language
        GROUP BY language, date_trunc('month', date);
  ''')

def rollback(cursor):
  cursor.execute('''
    DROP MATERIALIZED VIEW commit_by_language_monthly;
    DROP MATERIALIZED VIEW commit_by_language;
  ''')
