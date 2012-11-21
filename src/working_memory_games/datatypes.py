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


class Session(OOBTree):
    """ Session container, which holds daily gaming data for a single player
    for a single day """

    implements(ISession)

    @property
    def duration(self):
        total = datetime.timedelta(0)
        for game in self.values():
            total += getattr(game, "duration", datetime.timedelta(0))
        return total


class GameSession(OOBTree):
    """ Game session container, which holds daily gaming data for a single
    player in a single game (for a single day) """

    implements(IGameSession)
