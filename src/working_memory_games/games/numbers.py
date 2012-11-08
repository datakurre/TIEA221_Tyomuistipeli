# -*- coding: utf-8 -*-
""" Numbers game """

import random

from pyramid.view import view_config

from working_memory_games import game_config
from working_memory_games.games import Game

import logging
logger = logging.getLogger("working_memory_games")


@game_config()
class Numbers(Game):
    """ Numeropeli """

    @view_config(name="new")
    def new_numbers_game(self):
        """ Returns new game data """

        level = int(self.player_level)

        items = [random.sample(range(1, 10), 1)[0]
                 for i in range(level)]

        return {
            "level": level,
            "items": items
        }
