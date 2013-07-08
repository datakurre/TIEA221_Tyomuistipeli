# -*- coding: utf-8 -*-
import datetime
import logging
import random

from pyramid.view import view_config
from working_memory_games import game_config
from working_memory_games.games import Game


logger = logging.getLogger("working_memory_games")


@game_config()
class Blocks(Game):
    """Laatikkopeli
    """

    can_assist = True

    @view_config(name="new")
    def new_numbers_game(self):
        """Returns new game data
        """

        self.session.last_start = datetime.datetime.utcnow()

        level = self.calculate_level(9)  # int(self.session.level)

        items = [random.sample(range(1, 10), 1)[0]
                 for i in range(level)]

        return {
            "assisted": self.app.get_next_game()['assisted'],
            "level": level,
            "items": items
        }
