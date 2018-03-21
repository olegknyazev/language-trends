def perform(cursor):
  cursor.execute(
    '''CREATE TABLE commits_per_day (
        repository_id varchar(40)
          REFERENCES repositories ON DELETE CASCADE ON UPDATE CASCADE,
        date date NOT NULL,
        commit_count integer NOT NULL DEFAULT 0)''')
