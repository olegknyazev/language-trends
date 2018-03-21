def perform(cursor):
  cursor.execute(
    '''CREATE TABLE repositories (
        id varchar(40) PRIMARY KEY,
        name varchar(40) NOT NULL,
        language varchar(40) NOT NULL)''')

def rollback(cursor):
  cursor.execute('DROP TABLE repositories;')
