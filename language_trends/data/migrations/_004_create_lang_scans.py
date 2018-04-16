def perform(cursor):
  cursor.execute('''
    CREATE TABLE lang_scans (
      lang varchar(40) PRIMARY KEY,
      actual_by date NOT NULL);''')

def rollback(cursor):
  cursor.execute('DROP TABLE lang_scans;')
