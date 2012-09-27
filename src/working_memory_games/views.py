# -*- coding: utf-8 -*-
""" Root view definitions """

import os
import time
import json

from BTrees.OOBTree import OOBTree

from pyramid.response import FileResponse
from pyramid.httpexceptions import HTTPBadRequest

from working_memory_games.interfaces import (
    IApplication,
    IGame
)


def favicon(request):
    """ /favicon.ico from ./favicon.ico """
    here = os.path.dirname(__file__)
    icon = os.path.join(here, 'favicon.ico')
    return FileResponse(icon, request=request)


def robots(request):
    """ /robots.txt from ./robots.txt """
    here = os.path.dirname(__file__)
    robots = os.path.join(here, 'robots.txt')
    return FileResponse(robots, request=request)


def menu(context, request):
    """ Main menu """

    app = IApplication(context)

    games = []
    for name, game in app.games.items():
        games.append({
            "name": name,
            "title": game.title
        })

    return {"games": games}


def load(context, request):
    """ Returns current player data """

    game = IGame(context)
    player = game.player

    if not game.__name__ in player:
        player[game.__name__] = OOBTree()

    data = player[game.__name__]

    return dict(data.items())


def save(context, request):
    """ Save new data for player """

    game = IGame(context)
    player = game.player

    if not game.__name__ in player:
        player[game.__name__] = OOBTree()

    store = player[game.__name__]

    try:
        data = json.decode(request.params.get("data", None))
    except:
        raise HTTPBadRequest()

    if not data:
        raise HTTPBadRequest()

    key = str(time.time())
    store[key] = data

    return True
