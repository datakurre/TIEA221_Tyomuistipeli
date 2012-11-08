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

import logging
logger = logging.getLogger("working_memory_games")


class Game(object):
    """ Game base class """

    implements(IGame)

    start_level = 3.0

    def __init__(self, app, name=None):
        self.app = app
        self.name = name or self.__class__.__name__.lower()
        self.session = None

    def set_session(self, session):
        name = self.name

        if not name in session:
            session[name] = OOBTree()

        if not "level" in session[name]:
            session[name]["level"] = Length(self.start_level)

        self.session = session
        self.session_data = session[name]

    def get_session_level(self):
        assert self.session, (u"Session has not been set yet. "
                              u"Call ``set_session`` to set session.")

        return self.session_data["level"]()

    def set_session_level(self, value):
        assert self.session, (u"Session has not been set yet. "
                              u"Call ``set_session`` to set session")

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

@view_config(route_name="traversal",
             name="new", context=Story, renderer="json", xhr=True)
def new_story_game(context, request):
    """ Return new game data """

    assert verifyObject(IGame, context)

    level = int(context.player_level)

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
