def update(c):
  c.execute(
    '''CREATE TABLE IF NOT EXISTS repositories (
        id varchar(40) PRIMARY KEY,
        name varchar(40) NOT NULL,
        language varchar(40) NOT NULL)''')
