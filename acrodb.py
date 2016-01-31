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
    args = (acronym.upper(),)
    cursor = _conn.execute("SELECT * from ACRONYMS WHERE ACRONYM=?", args)
    for row in cursor:
        results.append(row[1])
    print("Found %s results in local database" % len(results))
    return results

def addAcronyms(acronym, descriptions, more_results):
    added = 0
    for desc in descriptions:
        if added == 10:
            break
        try:
            args = (acronym.upper(), desc)
            _conn.execute("INSERT INTO ACRONYMS (ACRONYM,DESCRIPTION) VALUES (?, ?)", args)
            print "Added a new acronym and description to local database"
            added += 1
        except sqlite3.IntegrityError:
            print "Did not add new acronym since it was already in table"

    try:
        more = 0
        if more_results == True:
            more = 1
        args = (acronym.upper(), 1, more)
        _conn.execute("INSERT INTO POPULARITY VALUES (?, ?, ?);", args)
    except sqlite3.IntegrityError:
        print "Did not add new acronym to Popularity table since it was already in table"

    print("Added %s new acronyms to database" % str(added))
    commit()

# Returns hits and if more results are on abbreviations.com (hits, more)
def getPopularity(acronym):
    args = (acronym.upper(),)
    cursor = _conn.execute("SELECT * from POPULARITY WHERE ACRONYM=?", args)
    row = cursor.fetchone()
    more = False
    print("row[2]=%d" % row[2])
    if int(row[2]) == 1:
        print "Set to true"
        more = True
    return row[1], more

def increasePopularity(acronym):
    views, more = getPopularity(acronym)
    views += 1
    args = (views, acronym.upper())
    cursor = _conn.execute("UPDATE POPULARITY set HITS=? WHERE ACRONYM=?", args)
    commit()
    print "Popularity of %s updated to %d" % (acronym.upper(), views)

if __name__ == "__main__":
    try:
        _conn.execute('''CREATE TABLE ACRONYMS
            (ACRONYM TEXT NOT NULL,
            DESCRIPTION TEXT NOT NULL,
            PRIMARY KEY (ACRONYM, DESCRIPTION));''')
        print "Acronym table created successfully"
    except sqlite3.OperationalError:
        print "Acronym Table already exists, did not create table"
    try:
        _conn.execute('''CREATE TABLE POPULARITY
            (ACRONYM TEXT PRIMARY KEY NOT NULL,
            HITS INTEGER NOT NULL,
            MORE_RESULTS BOOLEAN NOT NULL);''')
        print "Popularity table created successfully"
    except sqlite3.OperationalError:
        print "Popularity Table already exists, did not create table"
    close()
