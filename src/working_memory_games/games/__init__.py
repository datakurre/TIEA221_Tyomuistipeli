# -*- coding: utf-8 -*-
""" Base implementation for games """

import datetime

from pyramid.view import (
    view_config,
    view_defaults
)

from zope.interface import implements

from working_memory_games.datatypes import (
    OOBTree,
    Length
)

from working_memory_games.interfaces import IGame

import logging
logger = logging.getLogger("working_memory_games")


@view_defaults(context=IGame, route_name="traversal", xhr=True)
class Game(object):
    """ Game base class """

    implements(IGame)

    name = u""
    app = None
    session = None

    start_level = 3.0

    def __init__(self, context, request=None):
        # Support initialization as view class instance
        if issubclass(context.__class__, self.__class__):
            self.__dict__.update(context.__dict__)
            return

        # Continue initialization as game class instance
        self.name = unicode(self.__class__.__name__.lower(), "ascii")
        self.app = context
        self.session = None

    def set_session(self, player_session):
        game_session = player_session.get(self.name)
        if game_session is None:
            game_session = player_session[self.name] = OOBTree()

        if not hasattr(game_session, "level"):
            game_session.level = Length(self.start_level)

        self.session = game_session

    def get_session_level(self):
        assert self.session is not None, (
            u"Session has not been set yet. "
            u"Call ``set_session`` to set session."
        )

        return self.session.level()

    def set_session_level(self, value):
        assert self.session is not None, (
            u"Session has not been set yet. "
            u"Call ``set_session`` to set session."
        )

        current = self.session_level
        delta = value - current
        self.session.level.change(delta)

    session_level = property(get_session_level, set_session_level)

    @view_config(name="pass", renderer="../templates/save_pass.html")
    def save_pass(self):
        """ Saves successful game """

        key = str(datetime.datetime.utcnow())
        self.session[key] = {
            "level": self.session_level,
            "pass": True
        }

        self.session_level += 0.5

        return {}

    @view_config(name="fail", renderer="../templates/save_fail.html")
    def save_fail(self):
        """ Saves failed game """

        key = str(datetime.datetime.utcnow())
        self.session[key] = {
            "level": self.session_level,
            "pass": False
        }

        self.session_level = max(self.session_level - 0.5, 2.0)

        return {}

    @view_config(name="dump", renderer="json", xhr=False)
    def dump_saved_data(self):
        """ Returns current session data """

        return dict(self.session.items())
