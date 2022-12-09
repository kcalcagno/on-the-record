#!/usr/bin/python3

import sqlite3
import sys
from hoops import Game

conn = sqlite3.connect('hoops.db')
conn.row_factory = sqlite3.Row

gameId = sys.argv[1]

game = Game.loadById(gameId, conn)
game.clear(conn)
