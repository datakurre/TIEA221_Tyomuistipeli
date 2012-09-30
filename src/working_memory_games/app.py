#-*- coding: utf-8 -*-
""" Application """

import re
import uuid

from zope.interface import implements
from zope.interface.verify import verifyObject

from pyramid.renderers import get_renderer

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


def add_base_template(event):
    """ Adds base template for Chameleon renderer """

    base_template = get_renderer("templates/base_template.pt").implementation()

    request = event["request"]
    path = re.sub("/*$", "", request.path)

    event.update({
        "base_template": base_template,
        "base_url": request.application_url,
        "context_url": "%s%s" % (request.application_url, path),
    })


def list_all(context, request):
    """ List all games """

    app = IApplication(context)

    games = []
    for name, game in app.games.items():
        games.append({
            "name": name,
            "title": game.title
        })

    cmp_by_title = lambda x, y: cmp(x["title"], y["title"])

    return {
        "games": sorted(games, cmp=cmp_by_title)
    }


def dump_saved_data(context, request):
    """ Return current player data """

    assert verifyObject(IApplication, context)

    return dict(context.player.items())
