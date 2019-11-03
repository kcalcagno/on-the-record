#!/usr/bin/python

import sqlite3
import sys

filename = sys.argv[1]
with open(filename, 'r') as sqlfile:
    script = sqlfile.read()
    con = sqlite3.connect('hoops.db')
    cur = con.cursor()
    cur.executescript(script)
