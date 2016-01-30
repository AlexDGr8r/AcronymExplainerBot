#!/usr/bin/env python

import sqlite3

_conn = sqlite3.connect('acronyms.db')
print "Connected to database successfully"

def close():
    _conn.close()
    print "Connection closed"

def commit():
    _conn.commit()
    print "Committed local changes"

def getAcronym(acronym):
    results = []
    cursor = _conn.execute("SELECT * from ACRONYMS WHERE ACRONYM = '%s'" % acronym.upper())
    for row in cursor:
        row_dict = {'Acronym' : row[0], 'Description' : row[1]}
        results.append(row_dict)
    print("Found %s results in local database" % len(results))
    return results

def addAcronyms(acronyms):
    added = 0
    for row_dict in acronyms:
        try:
            _conn.execute("INSERT INTO ACRONYMS (ACRONYM,DESCRIPTION) VALUES ('%s', '%s')" % (row_dict['Acronym'].upper(), row_dict['Description']))
            print "Added a new acronym and description to local database"
            added += 1
        except sqlite3.IntegrityError:
            print "Did not add new acronym since it was already in table"
    print("Added %s new acronyms to database" % str(added))
    commit()

if __name__ == "__main__":
    try:
        _conn.execute('''CREATE TABLE ACRONYMS
            (ACRONYM TEXT NOT NULL,
            DESCRIPTION TEXT NOT NULL,
            PRIMARY KEY (ACRONYM, DESCRIPTION));''')
        print "Acronym table created successfully"
    except sqlite3.OperationalError:
        print "Table already exists, did not create table"
    close()
