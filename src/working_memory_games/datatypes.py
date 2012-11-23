# -*- coding: utf-8 -*-
""" Persistent types """

import datetime

from zope.interface import implements

from BTrees.OOBTree import OOBTree as OOBTreeBase
from BTrees.Length import Length as LengthBase

from working_memory_games.interfaces import (
    IPlayers,
    IPlayer,
    ISession,
    IGameSession
)

import logging
import random
import uuid
logger = logging.getLogger("working_memory_games")


class OOBTree(OOBTreeBase):
    """ OOBTree, which can also hold direct persistent attributes and can be
    JSON-serialized """

    ###
    # Add persistent attribute support for OOBTree
    #
    # Loading attribute and mapping state in an OOBTree subclass by ZODB
    # requires custom __getstate__() and __setstate__() to handle load/save of
    # object state for both attributes and mapping keys/values (BTree buckets).
    # [wraps superclass __getstate__ and __setstate__ methods]
    #
    # http://pastie.org/1732745
    #

    def __getstate__(self):
        tree_state = super(OOBTree, self).__getstate__()
        attr_state = [(k, v) for k, v in self.__dict__.items()
                      if not (k.startswith('_v_') or k.startswith('__'))]
        return (tree_state, attr_state)

    def __setstate__(self, v):
        tree_state = v[0]
        attr_state = v[1]
        for k, v in attr_state:
            setattr(self, k, v)
        super(OOBTree, self).__setstate__(tree_state)

    ###

    def __json__(self, request):
        return dict(self.items())


class Length(LengthBase):
    """ Generic integer based length, which handles conflict resolutiosn and
    can be JSON-serialized """

    def __json__(self, request):
        return self()


class Players(OOBTree):
    """ Players container, which contains individual player data objects """

    implements(IPlayers)

    def get_player(self, player_id):
        """ Returns player or None if not found."""
        return get(player_id)

    def create_player(self, name):
        """ Creates a new Player """
        player_id = str(uuid.uuid4())
        self[player_id] = Player(name)


class Player(OOBTree):
    """ Player container, which holds details and game sessions for a single
    player """

    implements(IPlayer)

    def __init__(self, name):
        super(Player, self).__init__()
        self.name = name

    @property
    def duration(self):
        total = datetime.timedelta(0)
        for session in self.values():
            total += getattr(session, "duration", datetime.timedelta(0))
        return total

    def session(self, games):
        """ Creates a new Session for today if needed. Always returns
        a session with games shuffled in random order."""
        today = str(datetime.datetime.utcnow().date())
        if not self.has_key(today):
            self[today] = Session(games)
        return self[today]

    def get_sessions(self):
        return map(lambda x: self[x], sorted(self.keys()))


class Session(OOBTree):
    """ Session container, which holds daily gaming data for a single player
    for a single day """

    implements(ISession)

    def __init__(self, games):
        super(Session, self).__init__()
        self.order = games
        random.shuffle(self.order)


    @property
    def duration(self):
        total = datetime.timedelta(0)
        for game in self.values():
            total += getattr(game, "duration", datetime.timedelta(0))
        return total

    def get_game(self, name):
        if not self.has_key(name):
            self[name] = GameSession()
        return self[name]


class GameSession(OOBTree):
    """ Game session container, which holds daily gaming data for a single
    player in a single game (for a single day) """

    implements(IGameSession)

    def __init__(self):
        super(GameSession, self).__init__()
        self.duration = datetime.timedelta(0)

    def get_plays(self):
        """ Return all game plays (tries) of this game on today."""
        return map(lambda x: self[x], sorted(self.keys()))

    def save_pass(self, gameinfo):
        time_key = str(datetime.datetime.utcnow())
        self[time_key] = gameinfo

    def save_fail(self, gameinfo):
        time_key = str(datetime.datetime.utcnow())
        self[time_key] = gameinfo

