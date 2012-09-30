# -*- coding: utf-8 -*-
""" Games """

import datetime

import random

from zope.interface import implements
from zope.interface.verify import verifyObject

from working_memory_games.persistent import (
    OOBTree,
    Length
)

from working_memory_games.interfaces import IGame


class Game(object):
    """ Game base class """

    start_level = 3.0

    def __init__(self, player):
        name = self.name

        if not name in player:
            player[name] = OOBTree()

        if not "level" in player[name]:
            player[name]["level"] = Length(self.start_level)

        self.player = player
        self.player_data = player[name]

    def get_player_level(self):
        return self.player_data["level"]()

    def set_player_level(self, value):
        current = self.player_level
        delta = value - current
        self.player_data["level"].change(delta)

    player_level = property(get_player_level, set_player_level)

    def get_new_game_items(self):

        level = int(self.player_level)
        count = 6

        if level <= count:
            items = random.sample(range(count), level)
        else:
            items = random.sample(range(count) * 2, level)

        return items


class Race(Game):
    """ Car race """

    implements(IGame)

    name = "race"
    title = u"Autokisa"


class Machines(Game):
    """ Machines """

    implements(IGame)

    name = "machines"
    title = u"Koneita"


class Numbers(Game):
    """ Numbers """

    implements(IGame)

    name = "numbers"
    title = u"Numeroita"

    def get_new_game_items(self):

        level = int(self.player_level)

        items = [random.sample(range(1, 10), 1)[0]
                 for i in range(level)]

        return items


def view(context, request):
    return {}


def new_game(context, request):
    """ Return new game data """

    assert verifyObject(IGame, context)

    level = context.player_level
    items = context.get_new_game_items()

    return {
        "level": level,
        "items": items
    }


def save_pass(context, request):
    """ Save successful game """

    assert verifyObject(IGame, context)

    key = str(datetime.datetime.now())
    context.player_data[key] = {
        "level": context.player_level,
        "pass": True
    }

    context.player_level += 0.5

    return {}


def save_fail(context, request):
    """ Save failed game """

    assert verifyObject(IGame, context)

    key = str(datetime.datetime.now())
    context.player_data[key] = {
        "level": context.player_level,
        "pass": False
    }

    context.player_level = max(context.player_level - 0.5, 2.0)

    return {}


def dump_saved_data(context, request):
    """ Return current player data """

    assert verifyObject(IGame, context)

    return dict(context.player_data.items())
