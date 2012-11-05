# -*- coding: utf-8 -*-
""" Numbers """

import random

from pyramid.view import view_config

from zope.interface.verify import verifyObject

from working_memory_games import game_config
from working_memory_games.interfaces import IGame
from working_memory_games.games import Game


@game_config()
class Numbers(Game):
    """ Numbers """

    name = "numbers"
    title = u"Numeroita"


@view_config(route_name="traversal",
             name="new", context=Numbers, renderer="json", xhr=True)
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
