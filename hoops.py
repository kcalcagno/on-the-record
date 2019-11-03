#!/usr/bin/python

import sqlite3
import pystache
import re

class Game(object):
    games = dict()
    
    def __init__(self):
        self.penalty = 0
        self.predictions = []
    
    @classmethod
    def loadAll(clazz, conn):
        cur = conn.cursor()
        for row in cur.execute('select * from game'):
            game = clazz.load(row)
            clazz.games[game.gameId] = game

    @classmethod
    def loadById(clazz, gameId, conn):
        cur = conn.cursor()
        cur.execute('select * from game where game_id = :id', {'id': gameId})
        return clazz.load(cur.fetchone())

    @classmethod
    def load(clazz, row):
        game = clazz()
        game.gameId = row['game_id']
        game.opponent = row['opponent']
        game.shortName = row['short_name']
        game.conference = bool(row['conference'])
        game.ndScore = row['nd_score']
        game.oppScore = row['opp_score']
        game.filename = 'game%02d.html' % (game.gameId)
        return game;

    @classmethod
    def dump(clazz):
        for game in list(clazz.games.values()):
            print(game.gameId, game.opponent, game.ndScore, game.oppScore)
            
    def save(self, conn):
        query = '''update game set nd_score = :nd, opp_score = :opp
                   where game_id = :id'''
        params = {'id': self.gameId, 'nd': self.ndScore, 'opp': self.oppScore}
        conn.execute(query, params)
        conn.commit()

    def savePicks(self, conn):
        query = 'insert into prediction values (:game, :poster, :nd, :opp)'
        conn.executemany(query, self.generatePickData())
        conn.commit()

    def generatePickData(self):
        for pick in self.predictions:
            yield {'game': self.gameId, 'poster': pick.poster.posterId,
                   'nd': pick.ndScore, 'opp': pick.oppScore}

    def calculate(self):
        for pick in self.predictions:
            pick.calculate()
        self.predictions.sort(key=lambda p: p.sortkey())

        prevPick = None
        for rank, pick in enumerate(self.predictions, start=1):
            if prevPick and pick.sortkey() == prevPick.sortkey():
                pick.gameRank = prevPick.gameRank
                pick.gameBonus = prevPick.gameBonus
            else:
                pick.gameRank = rank
                if rank <= 3:
                    pick.gameBonus = rank * 2 - 7
            prevPick = pick
        self.penalty = self.predictions[-1].score + 10
    
    def render(self):
        with open(self.filename, 'w') as output:
            output.write(pystache.render(self))


class Poster(object):
    posters = dict()

    def __init__(self, posterId=None, posterName=None, nameKey=None):
        self.posterId = posterId
        self.posterName = posterName
        if nameKey:
            self.nameKey = nameKey
        elif self.posterName:
            self.nameKey = self.getNameKey(self.posterName)
        self.predictions = dict()
        
    @classmethod
    def loadAll(clazz, conn):
        cur = conn.cursor()
        for row in cur.execute('select * from poster'):
            poster = clazz.load(row)
            clazz.posters[poster.posterId] = poster

    @classmethod
    def load(clazz, row):
        return clazz(row['poster_id'], row['poster_name'], row['name_key'])

    @classmethod
    def loadByName(clazz, name, conn, saveNew=False):
        cur = conn.cursor()
        cur.execute('select * from poster where name_key = :key',
                    {'key': clazz.getNameKey(name)})
        row = cur.fetchone()
        if row:
            return clazz.load(row)
        elif saveNew:
            Poster(posterName=name).save(conn)
            return clazz.loadByName(name, conn)
        else:
            return None

    def save(self, conn):
        if self.posterId:
            query = '''update poster set poster_name = :name, name_key = :key
                       where poster_id = :id'''
            params = {'id': self.posterId, 'name': self.posterName,
                      'key': self.nameKey}
        else:
            query = '''insert into poster (poster_name, name_key)
                       values (:name, :key)'''
            params = {'name': self.posterName, 'key': self.nameKey}

        conn.execute(query, params)
        conn.commit()

    @staticmethod
    def getNameKey(name):
        return re.sub(r'\W', '', name).upper()

class Prediction(object):
    def __init__(self, game, poster, ndScore, oppScore):
        self.game = game
        self.poster = poster
        self.ndScore = ndScore
        self.oppScore = oppScore
        self.score = 0
        self.margin = 0
        self.points = 0
        self.penalty = 0
        self.bonus = 0
        self.gameRank = 0
        self.gameBonus = 0

    def calculate(self):
        gameMargin = self.game.ndScore - self.game.oppScore
        pickMargin = self.ndScore - self.oppScore
        self.margin = abs(gameMargin - pickMargin)
        
        self.points = (abs(self.game.ndScore - self.ndScore)
                       + abs(self.game.oppScore - self.oppScore))
        
        if gameMargin * pickMargin <= 0:
            self.penalty = 10
        ndScoreDiff = abs(self.game.ndScore - self.ndScore)
        oppScoreDiff = abs(self.game.oppScore - self.oppScore)
        if ndScoreDiff == 0:
            self.bonus -= 2
        elif ndScoreDiff == 1:
            self.bonus -= 1
        if oppScoreDiff == 0:
            self.bonus -= 2
        elif oppScoreDiff == 1:
            self.bonus -= 1
        if ndScoreDiff == 0 and oppScoreDiff == 0:
            self.bonus = -5

        self.score = self.margin + self.points // 4 + self.penalty + self.bonus

    def sortkey(self):
        return (self.score, self.penalty, self.margin, self.points)


if __name__ == '__main__':
    conn = sqlite3.connect('hoops.db')
    conn.row_factory = sqlite3.Row

    Game.loadAll(conn)
    Game.dump()
