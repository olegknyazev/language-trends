def perform(cursor):
  cursor.execute('ALTER TABLE repositories ALTER COLUMN name TYPE varchar(100);')

def rollback(cursor):
  cursor.execute('ALTER TABLE repositories ALTER COLUMN name TYPE varchar(40);')
