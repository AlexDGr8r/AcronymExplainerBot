#!/usr/bin/env python

import sqlite3

_conn = sqlite3.connect('acronyms.db')
print "Connected to database successfully"

def close():
    _conn.close()
    print "Connection closed"

if __name__ == "__main__":
    try:
        _conn.execute('''CREATE TABLE ACRONYMS
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ACRONYM TEXT NOT NULL,
            DESCRIPTION TEXT NOT NULL);''')
        print "Acronym table created successfully"
    except sqlite3.OperationalError:
        print "Table already exists, did not create table"
    close()
