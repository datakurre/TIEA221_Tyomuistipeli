# -*- coding: utf-8 -*-
""" Base implementation for games """

from __future__ import division
from numpy import (
    arange,
    argmax,
    exp,
    log,
    where
)
from numpy.random import random

import datetime

from pyramid.view import (
    view_config,
    view_defaults
)

from zope.interface import implements

from working_memory_games.interfaces import IGame

import logging
logger = logging.getLogger("working_memory_games")


@view_defaults(context=IGame, route_name="traversal", xhr=True)
class Game(object):
    """ Game base class """

    implements(IGame)

    name = u""
    app = None
    session = None

    day_limit = 3       # How many games can be played during a daily session.
    can_assist = False  # Can the game assist player.
    start_level = 3.0   # Start level.

    def __init__(self, context, request=None):
        # Support initialization as view class instance
        if issubclass(context.__class__, self.__class__):
            self.__dict__.update(context.__dict__)
            return

        # Continue initialization as game class instance
        self.name = unicode(self.__class__.__name__.lower(), "ascii")
        self.app = context

    @property
    def player(self):
        return self.app.get_current_player()

    @property
    def session(self):
        player_session = self.app.get_current_session()

        if player_session is None:
            logger.debug('player session is None!')
            # TODO: Create implicit guest player here!
            from pyramid.httpexceptions import HTTPNotFound
            raise HTTPNotFound

        game_session = player_session.get_game(self.name)

        if not hasattr(game_session, "duration"):
            game_session.duration = datetime.timedelta(0)

        return game_session

    def get_last_plays(self, n=None):
        """Return last n levels for the game for the current player
        in reverse chronological order

        """
        if n is None:
            n = 10  # or some class property

        ret = []

        player = self.app.get_current_player()

        for session in reversed(player.get_sessions()):

            game = session.get_game(self.name)

            if game is None:
                continue

            for play in reversed(game.get_plays()):
                ret.append(play)

                if len(ret) == n:
                    break

            if len(ret) == n:
                break

        return ret

    def calculate_level(self, choises_N):
        """ Use jvk's adaptation to calculate the next level """

        # Mahdolliset tuntemattoman arvot
        kvals = arange(1, 21)

        # Mahdolliset n:n arvot
        nvals = arange(2, 20)

        def psi(k, n):
            # Todenmukaisessa mallissa on aina oltava pieni todennäköisyys
            # saada vahingossa väärin vaikka osaisi.  Kaavassa on hihasta
            # ravistettuna 5% vahinkotodennäköisyys ja lisäksi hatusta vedetty
            # 5% arvaustodennäköisyys, eli todennäköisyys jolla huonoinkin
            # pelaaja saa tehtävän oikein (tämän voi useimmiten päätellä
            # tehtävästä, esimerkiksi jos valitaan n:stä vaihtoehdosta, on
            # arvaustodennäköisyys 1/n).

            # 5% muistivirheitä (ref Memory book)
            gamma = 1. / 4. ** n
            return gamma + (1 - gamma - 0.05) / (1 + exp(n - k))

        p0 = 1.0 / where(kvals > 2, kvals, 3) ** 2
        p0 *= 1 / sum(p0)

        def update(p, n, res):
            if res:
                p = p * psi(kvals, n)
            else:
                p = p * (1 - psi(kvals, n))
            return p * (1 / sum(p))

        def entropy(p):
            return -sum(p * log(p + 1e-100)) / log(2)

        def simulate_result(n):
            p_succ = psi(true_k, n)
            return random() < p_succ

        def expected_gain(p, n, child_friendly=False):
            # oikean vastauksen estimoitu todennäköisyys
            p_succ = sum(p * psi(kvals, n))

            # väärän vastauksen estimoitu todennäköisyys
            p_fail = 1 - p_succ

            # entropian odotusarvo vastauksen jälkeen
            expected_entropy = (p_succ * entropy(update(p, n, 1))
                                + p_fail * entropy(update(p, n, 0)))

            # entropian pieneniminen  = saatu informaatio
            gain = entropy(p) - expected_entropy

            if child_friendly:
                # lapsiystävällinen versio:
                # mitataan saadun informaatiomäärän odotusarvo
                # suhteessa "hinnan" odotusarvoon, missä hinta
                # on määritelty siten, että väärä vastaus
                # maksaa yhden yksikön
                gain /= n  # p_fail

            return gain

        # simuloitu todellinen pelaajan parametri
        true_k = 7

        # käytetäänkö "lapsiystävällistä versiota"
        child_friendly = True

        p = p0
        # i = 0
        #n = 3  # default if not games yet
        last_plays = sorted(
            self.get_last_plays(20),
            cmp=lambda x, y: cmp(x.get('start') or datetime.datetime.now(),
                                 y.get('start') or datetime.datetime.now())
        )
        for play in last_plays:
            #print play
            n = play['level']
            res = play['pass']
            p = update(p, n, res)
            #print 'p_%d = [%s]' % (i, ' '.join('%.2f' % prob for prob in p))

        #print
        #print 'p_%d = [%s]' % (i, ' '.join('%.2f' % prob for prob in p))
        gains = [expected_gain(p, n, child_friendly=child_friendly)
                 for n in nvals]

        #print 'Expected gains in bits for n = %s:' % nvals
        #print '[%s]' % (' '.join('%.3f' % g for g in gains))
        n = nvals[argmax(gains)]
        if len(last_plays) == 0:
            n = 3
        elif n > last_plays[0]['level'] + 2:
            n = last_plays[0]['level'] + 2
        logger.info('Best n to present next: %s' % n)

        self.session.level = n
        return int(n)  # remove numpy-reperesentation

    @view_config(name="runanimation", renderer="json", xhr=False)
    def run_animation(self):
        logger.debug('run animation =>')
        ret = len(self.session.get_plays()) == 0
        if 'testAnimation' in self.app.request.params:
            ret = True
        logger.debug('run animation <= ')
        return {
            "animation": ret
        }

    @view_config(name="pass", renderer="../templates/save_pass.html")
    def save_pass(self):
        """ Saves successful game """
        items = self.app.request.json_body
        duration = datetime.datetime.utcnow() - self.session.last_start
        self.session.duration += duration
        self.session.save_pass({
            "level": self.session.level,
            "pass": True,
            "items": items,
            "start": self.session.last_start,
            "duration": duration
        })
        player_session = self.app.get_current_session()
        player_session.order.pop(0)  # Remove played game form the session.

        values = {
            "game": self.name,
            "game_over": True
        }
        if len(player_session.order) > 0:
            if player_session.order[0]["game"] == self.name:
                values["game_over"] = False
        return values

    @view_config(name="fail", renderer="../templates/save_fail.html")
    def save_fail(self):
        """ Saves failed game """

        items = self.app.request.json_body
        duration = datetime.datetime.utcnow() - self.session.last_start
        self.session.duration += duration
        self.session.save_fail({
            "level": self.session.level,
            "pass": False,
            "items": items,
            "start": self.session.last_start,
            "duration": duration
        })
        player_session = self.app.get_current_session()
        player_session.order.pop(0)  # Remove played game form the session.

        values = {
            "game": self.name,
            "game_over": True
        }
        if len(player_session.order) > 0:
            if player_session.order[0]["game"] == self.name:
                values["game_over"] = False
        return values

    @view_config(name="game_over", renderer="../templates/game_over.html",
                 request_method="GET", xhr=False)
    def get_game_over(self):
        data = {}

        now = datetime.datetime.utcnow()
        today = datetime.datetime(*(now.timetuple()[:3]))
        all_plays = self.get_last_plays()
        plays_today = [play for play in all_plays if
                       "start" in play and play.get("start") >= today]

        # When first play, stars = 2
        if len(all_plays) == len(plays_today):
            data["stars"] = 2
        # When level increased, stars = 3
        elif self.session.level > plays_today[-1]["level"]:
            data["stars"] = 3
        # When level decreased, stars = 1
        elif self.session.level < plays_today[-1]["level"]:
            data["stars"] = 1
        # Otherwise, stars = 2
        else:
            data["stars"] = 2

        # When session has not yet ended, return the next game
        session = self.app.get_current_session()
        if session.order:
            data["game"] = session.order[0]["game"]

        return data
