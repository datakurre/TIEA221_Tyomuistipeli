# -*- coding: utf-8 -*-
""" Pyramid application initialization and startup functions """

import uuid

from BTrees.OOBTree import OOBTree

from zope.interface import implements

from pyramid.config import Configurator

from pyramid_zodbconn import get_connection

from working_memory_games.interfaces import (
    IApplication,
    IPlayer,
    IGame
)

import logging
logger = logging.getLogger("working_memory_games")


class Application(object):
    """ Dynamic application root object (with traverse for available games) """

    implements(IApplication)

    def __init__(self, request):
        root = get_connection(request).root()

        if not "players" in root:
            root["players"] = OOBTree()

        players = root["players"]
        player_id = request.cookies.get("player_id")

        if not player_id or player_id not in players:
            player = Player()
            player_id = str(uuid.uuid4())
            players[player_id] = player
            logger.info("Created a new player '%s'", player_id)

        request.response.set_cookie("player_id", player_id,
                                     max_age=(60 * 60 * 24 * 365))

        registry = request.registry

        self.player = players[player_id]
        self.games = dict(registry.getAdapters((self.player,), IGame))

    def __getitem__(self, name):
        """ Returns the game registered with name """
        game = self.games[name]
        game.__name__ = name
        return game



class Player(OOBTree):
    """ Player """

    implements(IPlayer)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application """
    # Configure
    config = Configurator(root_factory=Application,
                          settings=settings)

    # Enable ZODB support
    config.include("pyramid_zodbconn")
    config.include("pyramid_tm")

    # Enable ZCML support
    config.include("pyramid_zcml")
    config.load_zcml("configure.zcml")

    # Make WSGI
    return config.make_wsgi_app()
