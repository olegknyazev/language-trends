def perform(cursor):
  cursor.execute('''
    CREATE TABLE repos (
      id varchar(40) PRIMARY KEY,
      name varchar(100) NOT NULL,
      lang varchar(40) NOT NULL)''')

def rollback(cursor):
  cursor.execute('DROP TABLE repos;')
