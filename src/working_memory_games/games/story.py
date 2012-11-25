# -*- coding: utf-8 -*-
""" Tarinapeli """

import random
import datetime

from pyramid.view import view_config

from working_memory_games import game_config
from working_memory_games.games import Game

import logging
logger = logging.getLogger("working_memory_games")


@game_config()
class Story(Game):
    """ Tarinapeli """

    @view_config(name="new")
    def new_story_game(self):
        """ Return new game data """

        self.session.last_start = datetime.datetime.utcnow()

        level = self.calculate_level(6)#int(self.session.level)

        story_parts = ('auto helikopteri kaivinkone kivi lehma linna '+
                       'luola majakka maki meri mokki pelle prinsessa '+
                       'puu pyora ranta rautatie teltta tie '+
                       'yksisarvinen').split(' ')

        items = random.sample(story_parts, level)
        logging.debug(items)
        order = items[1:]
        random.shuffle(order)
        logging.debug(order)

        # let's have 6 pictures where one is correct answer
        # TODO jvk, is this enough or too much?
        other_selections = {}
        for item in order:
            other_selections[item] = \
                [item] + random.sample(filter(lambda x: x!=item, story_parts), 5)
            random.shuffle(other_selections[item])
        logging.debug(other_selections)

        return {
            "level": level,
            "items": items,
            "query": order,
            "other_candidates": other_selections
        }
