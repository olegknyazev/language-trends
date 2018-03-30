def perform(cursor):
  cursor.execute('ALTER TABLE commits_per_day RENAME TO commits_by_repo;')

def rollback(cursor):
  cursor.execute('ALTER TABLE commits_by_repo RENAME TO commits_per_day;')
