#!/usr/bin/python3

import sqlite3
import pystache
from hoops import Game, Poster, Prediction

class Contest(object):
    def __init__(self, filename, title, conference, mulligans, disqualify):
        self.filename = filename + '.html'
        self.title = title
        self.conference = conference
        self.mulligans = mulligans
        self.plural = mulligans > 1
        self.disqualify = disqualify
        
        gameFilter = lambda g: g.ndScore and (not conference or g.conference)
        self.games = list(filter(gameFilter, iter(Game.games.values())))
        self.players = []
        self.active = len(self.games) > self.mulligans
        
    def calculate(self):
        for poster in Poster.posters.values():
            player = Player(poster, self)
            if len(self.games) - len(player.picks) < self.disqualify:
                self.players.append(player)
            else:
                continue
        
            for game in self.games:
                if game.gameId not in poster.predictions:
                    player.picks.append(ContestPick.penalty(game))
            player.picks.sort(key=lambda p: p.game.gameId)
            
            for pick in sorted(player.picks, key=lambda p: p.score, reverse=True)[0:self.mulligans]:
                pick.mulligan = True

            for pick in player.picks:
                if not pick.mulligan:
                    player.totalScore += pick.score
                if pick.bonus:
                    player.totalScore += pick.bonus

        self.players.sort(key=lambda p: p.totalScore)
        prevPlayer = None
        for rank, player in enumerate(self.players, start=1):
            if prevPlayer and player.totalScore == prevPlayer.totalScore:
                player.rank = prevPlayer.rank
            else:
                player.rank = rank
            prevPlayer = player

    def render(self):
        with open(self.filename, 'w') as output:
            output.write(pystache.render(self))


class Player(object):
    def __init__(self, poster, contest):
        self.name = poster.posterName
        self.picks = self.getPicks(poster.predictions, contest.conference)
        self.totalScore = 0
        self.rank = 0
        
    def getPicks(self, predictions, conference):
        pickFilter = lambda p: not conference or p.game.conference
        return [ContestPick(p) for p in filter(pickFilter, iter(predictions.values()))]


class ContestPick(object):
    def __init__(self, prediction=None):
        if prediction:
            self.game = prediction.game
            self.score = prediction.score
            self.bonus = prediction.gameBonus
        self.mulligan = False
        self.penalty = False
    
    @classmethod
    def penalty(clazz, game):
        pick = clazz()
        pick.game = game
        pick.score = game.penalty
        pick.bonus = None
        pick.penalty = True
        return pick

    def decoration(self):
        cssClass = ''
        if self.mulligan:
            cssClass += ' mulligan'
        if self.penalty:
            cssClass += ' penalty'
        return cssClass


class Index(object):
    def __init__(self, fullSeason, acc, misc):
        self.games = sorted(Game.games.values(), key=lambda g: g.gameId)
        self.fullSeasonActive = fullSeason.active
        self.accActive = acc.active
        self.misc = misc
        year = int(misc['year'])
        self.season = {
            'current': f'{year - 1}-{year}',
            'previous': f'{year - 2}-{year - 2001}',
            'prevDir': f'hoops{year - 2002}{year - 2001}'
        }

    def render(self):
        with open('index.html', 'w') as output:
            output.write(pystache.render(self))


def main():
    conn = sqlite3.connect('hoops.db')
    conn.row_factory = sqlite3.Row

    Poster.loadAll(conn)
    Game.loadAll(conn)

    picksCur = conn.cursor()
    picksQuery = 'select * from prediction where game_id = :id'
    for game in Game.games.values():
        if game.ndScore:
            for row in picksCur.execute(picksQuery, {'id': game.gameId}):
                poster = Poster.posters[row['poster_id']]
                prediction = Prediction(game, poster,
                                        row['nd_score'], row['opp_score'])
                game.predictions.append(prediction)
                poster.predictions[game.gameId] = prediction
            game.calculate()
            game.render()

    fullSeason = Contest('fullseason', 'Full Season Leaderboard', False, 2, 8)
    if fullSeason.active:
        fullSeason.calculate()
        fullSeason.render()

    acc = Contest('acc', 'ACC Leaderboard', True, 1, 4)
    if acc.active:
        acc.calculate()
        acc.render()

    miscCur = conn.execute('select property, value from miscellany')
    misc = dict(miscCur.fetchall())
    Index(fullSeason, acc, misc).render()

    
if __name__ == '__main__':
    main()
