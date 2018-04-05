def perform(cursor):
  cursor.execute('''
    CREATE TABLE commits (
        repo_id varchar(40)
          REFERENCES repos ON DELETE CASCADE ON UPDATE CASCADE,
        date date NOT NULL,
        commits_since_prev integer NOT NULL DEFAULT 0,
        commits_total integer NOT NULL DEFAULT 0,
      PRIMARY KEY (repo_id, date));''')

def rollback(cursor):
  cursor.execute('DROP TABLE commits;')
