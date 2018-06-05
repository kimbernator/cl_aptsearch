import sqlite3
import os

DB_INIT = """CREATE TABLE IF NOT EXISTS apts(
    id_submission INTEGER PRIMARY KEY,
    title TEXT,
    link TEXT
    );"""

DB_CHECK = ('SELECT id_submission, title from apts '
            'WHERE id_submission=?')

DB_RESET = "DROP TABLE apts;"

class CLDB:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.realpath('./data/clsearch.db'))
        self.c = self.conn.cursor()
        self.c.execute(DB_INIT)
        self.conn.commit()

    def insert(self, data_form):
        columns = ', '.join(data_form.keys())
        placeholders = ':'+', :'.join(data_form.keys())
        query = 'INSERT INTO apts (%s) VALUES (%s)' % (columns, placeholders)
        self.c.execute(query, data_form)
        self.conn.commit()

    def discover(self, id_submission):
        exists = self.c.execute(DB_CHECK, (id_submission,))
        existslen = len(self.c.fetchall())
        if existslen >= 1:
            return True
        else:
            return False

    def reset(self):
        self.c.execute(DB_RESET)
