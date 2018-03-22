def perform(cursor):
  cursor.execute(
    '''CREATE TABLE commits_per_day (
          repository_id varchar(40)
            REFERENCES repositories ON DELETE CASCADE ON UPDATE CASCADE,
          date date NOT NULL,
          commit_count integer NOT NULL DEFAULT 0,
        PRIMARY KEY (repository_id, date));''')

def rollback(cursor):
  cursor.execute('DROP TABLE commits_per_day;')
