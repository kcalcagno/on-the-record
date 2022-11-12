#!/usr/bin/python3

import re
import sys
import sqlite3
from hoops import Game, Poster, Prediction

pattern = re.compile(r'(^|.*?(?<=\D))(1?\d\d)\D.*?(?<=\D)(1?\d\d)(?=\D).* - \b(.+)\b  \d{4}-\d\d-\d\d');

conn = sqlite3.connect('hoops.db')
conn.row_factory = sqlite3.Row

filename = sys.argv[1]
scoreline = re.compile(r'@@ (\d+) (\d+) (\d+) @@')
with open(filename) as f:
    firstline = f.readline()

match = re.match(scoreline, firstline)
if match:
    gameId = match.group(1)
    ndScore = match.group(2)
    oppScore = match.group(3)
else:
    gameId = sys.argv[2]
    ndScore = sys.argv[3]
    oppScore = sys.argv[4]

game = Game.loadById(gameId, conn)
game.ndScore = ndScore
game.oppScore = oppScore
game.save(conn)

handles = dict()
with open(filename) as f:
    for line in f:
        match = re.match(pattern, line)
        if match:
            ndScore = match.group(2)
            oppScore = match.group(3)
            handle = match.group(4)

            poster = Poster.loadByName(handle, conn, saveNew=True)
            if poster.nameKey in handles:
                print('Duplicate handle: ', handle)
            else:
                handles[poster.nameKey] = poster

            if ndScore == oppScore:
                print('Illegal score: ', handle, ' ', ndScore, ' ', oppScore)

            prediction = Prediction(game, poster, ndScore, oppScore)
            game.predictions.append(prediction)

game.savePicks(conn)
