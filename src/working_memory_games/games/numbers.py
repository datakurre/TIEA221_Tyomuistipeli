# -*- coding: utf-8 -*-
""" Numbers """

import random

from zope.interface import implements
from zope.interface.verify import verifyObject

from working_memory_games.interfaces import IGame
from working_memory_games.games import Game


class Numbers(Game):
    """ Numbers """

    implements(IGame)

    name = "numbers"
    title = u"Numeroita"


def new_game(context, request):
    """ Return new game data """

    assert verifyObject(IGame, context)

    level = int(context.player_level)

    items = [random.sample(range(1, 10), 1)[0]
             for i in range(level)]

    return {
        "level": level,
        "items": items
    }
