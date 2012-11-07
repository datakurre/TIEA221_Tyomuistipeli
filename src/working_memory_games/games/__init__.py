# -*- coding: utf-8 -*-
""" Games """

import datetime

import random

from pyramid.view import view_config

from zope.interface import implements
from zope.interface.verify import verifyObject

from working_memory_games.datatypes import (
    OOBTree,
    Length
)

from working_memory_games import game_config
from working_memory_games.interfaces import IGame


class Game(object):
    """ Game base class """

    implements(IGame)

    start_level = 3.0

    def __init__(self, session):
        name = self.__class__.__name__.lower()

        if not name in session:
            session[name] = OOBTree()

        if not "level" in session[name]:
            session[name]["level"] = Length(self.start_level)

        self.session = session
        self.session_data = session[name]

    def get_session_level(self):
        return self.session_data["level"]()

    def set_session_level(self, value):
        current = self.session_level
        delta = value - current
        self.session_data["level"].change(delta)

    session_level = property(get_session_level, set_session_level)


@view_config(route_name="traversal",
             name="new", context=IGame, renderer="json", xhr=True)
def new_game(context, request):
    """ Return new game data """

    assert verifyObject(IGame, context)

    level = int(context.session_level)

    count = 6
    if level <= count:
        items = random.sample(range(count), level)
    else:
        items = random.sample(range(count) * 2, level)

    return {
        "level": level,
        "items": items
    }


@view_config(route_name="traversal",
             name="pass", context=IGame,
             renderer="../templates/save_pass.html", xhr=True,)
def save_pass(context, request):
    """ Save successful game """

    assert verifyObject(IGame, context)

    key = str(datetime.datetime.now())
    context.session_data[key] = {
        "level": context.session_level,
        "pass": True
    }

    context.session_level += 0.5

    return {}


@view_config(route_name="traversal",
             name="fail", context=IGame,
             renderer="../templates/save_fail.html", xhr=True)
def save_fail(context, request):
    """ Save failed game """

    assert verifyObject(IGame, context)

    key = str(datetime.datetime.now())
    context.session_data[key] = {
        "level": context.session_level,
        "pass": False
    }

    context.session_level = max(context.session_level - 0.5, 2.0)

    return {}


@view_config(route_name="traversal",
             name="dump", context=IGame, renderer="json", xhr=False)
def dump_saved_data(context, request):
    """ Return current session data """

    assert verifyObject(IGame, context)

    return dict(context.session_data.items())


register = game_config()


@register
class Race(Game):
    """ Rallipeli """


@register
class Machines(Game):
    """ Konepeli """


@register
class Story(Game):
    """ Tarinapeli """


@register
class Numbers(Game):
    """ Numeropeli """


@view_config(route_name="traversal",
             name="new", context=Numbers, renderer="json", xhr=True)
def new_numbers_game(context, request):
    """ Return new game data """

    assert verifyObject(IGame, context)

    level = int(context.player_level)

    items = [random.sample(range(1, 10), 1)[0]
             for i in range(level)]

    return {
        "level": level,
        "items": items
    }
