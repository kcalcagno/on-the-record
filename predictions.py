#!/usr/bin/python3

import argparse
import re
import sqlite3
from hoops import Game, Poster, Prediction

pattern = re.compile(r'(^|.*?(?<=\D))(1?\d\d)\D.*?(?<=\D)(1?\d\d)(?=\D).* - \b(.+)\b  \d{4}-\d\d-\d\d');

parser = argparse.ArgumentParser()
parser.add_argument('file', type=open)
parser.add_argument('gameId', type=int, nargs='?')
parser.add_argument('ndScore', type=int, nargs='?')
parser.add_argument('oppScore', type=int, nargs='?')
parser.add_argument('-c', '--clear', action='store_true')
args = parser.parse_args()

conn = sqlite3.connect('hoops.db')
conn.row_factory = sqlite3.Row

firstline = args.file.readline()
scoreline = re.compile(r'@@ (\d+) (\d+) (\d+) @@')

match = re.match(scoreline, firstline)
if match:
    gameId = match.group(1)
    ndScore = match.group(2)
    oppScore = match.group(3)
else:
    gameId = args.gameId
    ndScore = args.ndScore
    oppScore = args.oppScore

game = Game.loadById(gameId, conn)
if args.clear:
    game.clear(conn)
game.ndScore = ndScore
game.oppScore = oppScore
game.save(conn)

handles = dict()
for line in args.file:
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
