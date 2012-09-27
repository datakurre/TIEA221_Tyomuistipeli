# -*- coding: utf-8 -*-
"""Cars game"""

from zope.interface import implements

from working_memory_games.interfaces import IGame


class Game(object):
    """ Cars game """
    implements(IGame)

    title = u"Cars game"

    def __init__(self, player):
        self.player = player


def view(context, request):
    return {
        "common": "%s/static" % request.application_url,
        "context": "%s%s/static" % (request.application_url, request.path),
    }
