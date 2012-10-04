# -*- coding: utf-8 -*-
""" Car race """

from zope.interface import implements

from working_memory_games import game_config
from working_memory_games.interfaces import IGame
from working_memory_games.games import Game


@game_config(add_view=True, add_static_view=True)
class Race(Game):
    """ Car race """

    implements(IGame)

    name = "race"
    title = u"Autokisa"
