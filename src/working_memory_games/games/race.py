# -*- coding: utf-8 -*-
""" Rallipeli """

import random
import datetime

from pyramid.view import view_config

from working_memory_games import game_config
from working_memory_games.games import Game

import logging
logger = logging.getLogger("working_memory_games")


@game_config()
class Race(Game):
    """ Rallipeli """

    @view_config(name="new")
    def new_game(self):
        """ Returns new game data """

        self.session.last_start = datetime.datetime.utcnow()

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
