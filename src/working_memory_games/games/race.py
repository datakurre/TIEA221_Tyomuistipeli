# -*- coding: utf-8 -*-
""" Car race """

from working_memory_games import game_config
from working_memory_games.games import Game


@game_config()
class Race(Game):
    """ Car race """

    name = "race"
    title = u"Autokisa"
