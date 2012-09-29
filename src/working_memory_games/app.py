#-*- coding: utf-8 -*-
""" Application """

import uuid

from zope.interface import implements
from zope.interface.verify import verifyObject

from pyramid_zodbconn import get_connection

from working_memory_games.persistent import (
    OOBTree,
    Player
)

from working_memory_games.interfaces import (
    IApplication,
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
        return self.games[name]


def list_all(context, request):
    """ List all games """

    app = IApplication(context)

    games = []
    for name, game in app.games.items():
        games.append({
            "name": name,
            "title": game.title
        })

    return {
        "games": games
    }


def dump_saved_data(context, request):
    """ Return current player data """

    assert verifyObject(IApplication, context)

    return dict(context.player.items())
