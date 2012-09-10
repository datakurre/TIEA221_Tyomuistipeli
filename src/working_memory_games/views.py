# -*- coding: utf-8 -*-
""" Static view definitions """

import os

from pyramid.response import FileResponse

from working_memory_games.interfaces import IGame


def favicon(request):
    here = os.path.dirname(__file__)
    icon = os.path.join(here, 'static', 'favicon.ico')
    return FileResponse(icon, request=request)


def robots(request):
    here = os.path.dirname(__file__)
    robots = os.path.join(here, 'static', 'robots.txt')
    return FileResponse(robots, request=request)


def menu(context, request):
    registry = request.registry

    games = []
    for game in registry.getAdapters((context,), IGame):
       name, obj = game
       games.append({
            "name": name,
            "title": obj.title
       })

    return {"games": games}
