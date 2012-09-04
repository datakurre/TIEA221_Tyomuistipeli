# -*- coding: utf-8 -*-
"""Static view definitions"""

import os

from pyramid.response import FileResponse


def favicon(request):
    here = os.path.dirname(__file__)
    icon = os.path.join(here, 'static', 'favicon.ico')
    return FileResponse(icon, request=request)


def robots(request):
    here = os.path.dirname(__file__)
    robots = os.path.join(here, 'static', 'robots.txt')
    return FileResponse(robots, request=request)
