# -*- coding: utf-8 -*-
""" Story """

from working_memory_games import game_config
from working_memory_games.games import Game


@game_config()
class Story(Game):

    name = "story"
    title = u"Tarina"
