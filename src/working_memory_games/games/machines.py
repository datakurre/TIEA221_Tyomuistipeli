# -*- coding: utf-8 -*-
""" Konepeli """

import random

from pyramid.view import view_config

from working_memory_games import game_config
from working_memory_games.games import Game

import logging
logger = logging.getLogger("working_memory_games")


@game_config()
class Machines(Game):
    """ Konepeli """

    @view_config(name="new")
    def new_game(self):
        """ Returns new game data """

        level = int(self.session.level)

        count = 6
        if level <= count:
            items = random.sample(range(count), level)
        else:
            items = random.sample(range(count) * 2, level)

        return {
            "level": level,
            "items": items
        }
