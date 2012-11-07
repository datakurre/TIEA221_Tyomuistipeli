#-*- coding: utf-8 -*-
""" Application """

import re
import uuid

from pyramid.view import view_config
from pyramid.events import (
    BeforeRender,
    subscriber
)

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
    """ Dynamic application root object, which provides access to the
    database and enables traverse for available games """

    implements(IApplication)

    def __init__(self, request, root=None):
        registry = request.registry

        # Set up the database
        if root is None:
            root = get_connection(request).root()
        if not "players" in root:
            root["players"] = OOBTree()
        if not hasattr(root, "guests"):
            # XXX: Actually, guests should be stored into temporary database,
            # which would be clean when the server is restarted. I'll refactor
            # this and add a code to remove old guest-data as soon as I'll
            # figure out the proper ZEO-configuration... :) --asko
            root["guests"] = OOBTree()
        self.root = root

        # Continue to look up the current players
        players = root["players"]

        player_id = request.cookies.get("player_id")
        player_ids = request.cookies.get("player_ids", "").split(",")

        self.player = players.get(player_id)
        self.players = dict([(player_id, players.get(player_id))
                             for player_id in set(player_ids + [player_id])
                             if player_id in players])

        # Refresh cookies to give them more lifetime
        if self.player is not None:
            player_ids = self.players.keys()
            request.response.set_cookie("player_ids", ",".join(player_ids),
                                        max_age=(60 * 60 * 24 * 365))

        # Player not selected. Try guest:
        if self.player is None:
            guests = root["guests"]
            self.player = guests.get(player_id)

        self.games = dict(registry.getAdapters((self.player,), IGame))

    def __getitem__(self, name):
        """ Returns the game registered with name """
        if self.player:
            return self.games[name]
        else:
            raise KeyError


@subscriber(BeforeRender)
def add_base_template(event):
    """ Adds base template for Chameleon renderer """

    base_template =\
        get_renderer("templates/base_template.html").implementation()

    request = event["request"]
    path = re.sub("/*$", "", request.path)

    event.update({
        "base_template": base_template,
        "base_url": request.application_url,
        "current_url": "%s%s" % (request.application_url, path),
    })


@view_config(route_name="root", renderer="templates/index.html")
def root_view(request):
    return {}


@view_config(route_name="traversal", name="game", context=IApplication,
             renderer="templates/game.launchpage.html")
def game_view(context, request):
    return {}


@view_config(route_name="register", renderer="templates/register_player.html",
             request_method="GET")
def new_player_form(context, request):
    return {}


@view_config(route_name="traversal",
             name="liity", context=IApplication,
             renderer="templates/register_player.html",
             request_method="POST")
def handle_new_player(context, request):

    assert verifyObject(IApplication, context)

    name = request.params.get("name", "").strip()

    logging.debug(request.params)

    if name:
        player_id = str(uuid.uuid4())

        context.root["players"][player_id] = Player(name=name)


        request.response.set_cookie("player_id", player_id,
                                    max_age=(60 * 60 * 24 * 365))
        headers = ResponseHeaders({
            "Set-Cookie": request.response.headers.get("Set-Cookie")
        })

        return HTTPFound(location=request.application_url, headers=headers)
    else:
        return request.params


@view_config(route_name="traversal",
             name="list_players", context=IApplication,
             renderer="templates/list_players.html",
             request_method="GET", xhr="True")
def list_players(context, request):

    assert verifyObject(IApplication, context)

    players = []

    counter = 0
    for player_id, player in context.players.items():
        css = "gameBtn btn-%s" % counter
        css += " selected" if player is context.player else ""
        players.append({
            "id": player_id,
            "name": player.name,
            "css": css
        })
        counter += 1

    cmp_by_name = lambda x, y: cmp(x["name"], y["name"])

    return {
        "players": sorted(players, cmp=cmp_by_name),
    }


@view_config(route_name="traversal",
             name="select_player", context=IApplication,
             request_method="POST")
def handle_select_player(context, request):

    assert verifyObject(IApplication, context)

    player_id = request.params.get("player_id", "").strip()

    if player_id in context.root["players"]:
        request.response.set_cookie("player_id", player_id,
                                    max_age=(60 * 60 * 24 * 365))
        headers = ResponseHeaders({
            "Set-Cookie": request.response.headers.get("Set-Cookie")
        })
        return HTTPFound(location=request.application_url, headers=headers)
    else:
        return request.params


@view_config(route_name="traversal",
             name="select_guest", context=IApplication,
             request_method="POST")
def handle_select_guest(context, request):

    assert verifyObject(IApplication, context)

    player_id = str(uuid.uuid4())
    context.root["guests"][player_id] = Player(name=u"Guest")

    request.response.set_cookie("player_id", player_id,
                                max_age=(60 * 60 * 24 * 365))
    headers = ResponseHeaders({
        "Set-Cookie": request.response.headers.get("Set-Cookie")
    })

    return HTTPFound(location=request.application_url, headers=headers)


@view_config(route_name="traversal",
             name="dump", context=IApplication, renderer="json")
def dump_saved_data(context, request):
    """ Return current player data """

    assert verifyObject(IApplication, context)

    return dict(context.player.items())


#     games = []
#
#     for name, game in context.games.items():
#         games.append({
#             "name": name,
#             "title": game.title
#         })
#
#     cmp_by_title = lambda x, y: cmp(x["title"], y["title"])
#
#     return {
#         "games": sorted(games, cmp=cmp_by_title)
#     }
