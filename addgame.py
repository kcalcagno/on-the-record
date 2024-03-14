#!/usr/bin/python3

import hoops
from hoops import Game

opponent = input('Opponent: ')
shortName = input('Short name: ')
conference = input('Conference game (y/N)? ')

conn = hoops.connect()

games = Game.getAll(conn)
new_id = max(games.keys()) + 1

new_game = Game(gameId=new_id, opponent=opponent, shortName=shortName,
	            conference=conference in ('y', 'Y'))
new_game.create(conn)
