#-*- coding: utf-8 -*-
""" Application """

import re
import uuid

from zope.interface import implements
from zope.interface.verify import verifyObject

from webob.headers import ResponseHeaders

from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound

from pyramid_zodbconn import get_connection

from working_memory_games.datatypes import (
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
        registry = request.registry

        if not "players" in root:
            root["players"] = OOBTree()

        players = root["players"]

        player_id = request.cookies.get("player_id")
        player_ids = request.cookies.get("player_ids", "").split(",")

        self.player = players.get(player_id)
        self.players = dict([(player_id, players.get(player_id))
                             for player_id in set(player_ids + [player_id])
                             if player_id in players])

        self.games = dict(registry.getAdapters((self.player,), IGame))

        # Refresh cookies to give them more lifetime
        if self.player:
            player_ids = self.players.keys()
            request.response.set_cookie("player_ids", ",".join(player_ids),
                                        max_age=(60 * 60 * 24 * 365))

    def __getitem__(self, name):
        """ Returns the game registered with name """
        # TODO: Eventually, magical game selection will be implemented here.
        if self.player:
            return self.games[name]
        else:
            raise KeyError


def add_base_template(event):
    """ Adds base template for Chameleon renderer """

    base_template = get_renderer("templates/base_template.pt").implementation()

    request = event["request"]
    path = re.sub("/*$", "", request.path)

    event.update({
        "base_template": base_template,
        "base_url": request.application_url,
        "current_url": "%s%s" % (request.application_url, path),
    })


def select_player(context, request):

    assert verifyObject(IApplication, context)

    players = []
    games = []

    for player_id, player in context.players.items():
        players.append({
            "id": player_id,
            "name": player.name,
            "selected": player is context.player
        })

    for name, game in context.games.items():
        games.append({
            "name": name,
            "title": game.title
        })

    cmp_by_name = lambda x, y: cmp(x["name"], y["name"])
    cmp_by_title = lambda x, y: cmp(x["title"], y["title"])

    return {
        "players": sorted(players, cmp=cmp_by_name),
        "games": sorted(games, cmp=cmp_by_title)
    }


def handle_select_player(context, request):

    assert verifyObject(IApplication, context)

    root = get_connection(request).root()
    player_id = request.params.get("player_id", "").strip()

    if player_id in root["players"]:
        request.response.set_cookie("player_id", player_id,
                                    max_age=(60 * 60 * 24 * 365))
        headers = ResponseHeaders({
            "Set-Cookie": request.response.headers.get("Set-Cookie")
        })
        return HTTPFound(location=request.application_url, headers=headers)
    else:
        return request.params


def handle_new_player(context, request):

    assert verifyObject(IApplication, context)

    name = request.params.get("name", "").strip()

    if name:
        player_id = str(uuid.uuid4())

        root = get_connection(request).root()
        root["players"][player_id] = Player(name=name)

        request.response.set_cookie("player_id", player_id,
                                    max_age=(60 * 60 * 24 * 365))
        headers = ResponseHeaders({
            "Set-Cookie": request.response.headers.get("Set-Cookie")
        })

        return HTTPFound(location=request.application_url, headers=headers)
    else:
        return request.params


def dump_saved_data(context, request):
    """ Return current player data """

    assert verifyObject(IApplication, context)

    return dict(context.player.items())
