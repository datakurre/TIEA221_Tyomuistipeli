# -*- coding: utf-8 -*-
""" Base implementation for games """

import datetime

from pyramid.view import (
    view_config,
    view_defaults
)

from zope.interface import implements

from working_memory_games.interfaces import IGame
from working_memory_games.datatypes import GameSession

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

    @property
    def player(self):
        return self.app.get_current_player()

    @property
    def session(self):
        player_session = self.app.get_current_session()

        if player_session is None:
            # TODO: Create implicit guest player here!
            from pyramid.httpexceptions import HTTPNotFound
            raise HTTPNotFound

        game_session = player_session.get_game(self.name)

        # Look up the previous game session with the same game and
        # use the previous level as the start level for this game session.
        if not hasattr(game_session, "level"):
            player = self.app.get_current_player()
            session_keys = sorted(player.keys())
            for i in range(len(session_keys) - 2, -1, -1):
                previous_session = player[session_keys[i]]
                previous_game_session = previous_session.get(self.name)
                if previous_game_session is not None:
                    if hasattr(previous_game_session, "level"):
                        game_session.level = previous_game_session.level

        if not hasattr(game_session, "level"):
            game_session.level = self.start_level

        if not hasattr(game_session, "duration"):
            game_session.duration = datetime.timedelta(0)

        return game_session

    def get_last_levels(self, n=None, pass_only=False):
        """ Return last n levels for the game for the current player
        in reverse chronological order """

        if n is None:
            n = 10  # or some class property

        levels = []

        player = self.app.get_current_player()

        for session in reversed(player.get_sessions()):

            game = session.get_game(self.name)

            if game is None:
                continue

            for play in reversed(game.get_plays()):

                if play["pass"] or not pass_only:
                    levels.append(play["level"])

                if len(levels) == n:
                    break

            if len(levels) == n:
                break

        return levels

    @view_config(name="pass", renderer="../templates/save_pass.html")
    def save_pass(self):
        """ Saves successful game """
        items = self.app.request.json_body
        duration = datetime.datetime.utcnow() - self.session.last_start
        self.session.duration += duration
        self.session.save_pass({
            "level": self.session.level,
            "pass": True,
            "items": items,
            "duration": duration
        })
        return {}

    @view_config(name="fail", renderer="../templates/save_fail.html")
    def save_fail(self):
        """ Saves failed game """

        items = self.app.request.json_body
        duration = datetime.datetime.utcnow() - self.session.last_start
        self.session.duration += duration
        self.session.save_fail({
            "level": self.session.level,
            "pass": False,
            "items": items,
            "duration": duration
        })
        return {}

    @view_config(name="dump", renderer="json", xhr=False)
    def dump_saved_data(self):
        """ Returns current session data """

        return dict(self.session.items())
