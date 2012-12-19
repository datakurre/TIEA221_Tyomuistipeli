# -*- coding: utf-8 -*-
""" Silminnäkijä """

import random
import datetime

from pyramid.view import view_config

from working_memory_games import game_config
from working_memory_games.games import Game

import logging
logger = logging.getLogger("working_memory_games")


@game_config()
class Eyewitness(Game):
    """ Silminnäkijä """

    plateChars = "abcefghijklmnorstuvxyz".upper()

    @view_config(name="new")
    def new_witness_game(self):
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

    @view_config(name="save")
    def save_img(self):
        logging.info("AAAAAAA")
        b64 = self.app.request.params.get("imageData", "").split('base64,')[1]
        import base64, hashlib
        
        
        f = open('/tmp/'+ hashlib.sha224(b64).hexdigest()[0:10]+'.png', 'w')
        #logging.info(b64)
        logging.info(hashlib.sha224(b64).hexdigest()[0:10])
        f.write(base64.b64decode(b64))
        f.close()
        return {}
