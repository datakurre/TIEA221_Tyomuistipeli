# -*- coding: utf-8 -*-
""" Machines """


from working_memory_games import game_config
from working_memory_games.games import Game


@game_config()
class Machines(Game):
    """ Machines """

    name = "machines"
    title = u"Koneita"
