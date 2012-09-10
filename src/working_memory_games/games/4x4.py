# -*- coding: utf-8 -*-
"""4x4 game"""

from zope.interface import implements

from working_memory_games.interfaces import IGame


class Game(object):
    """ 4x4 game """
    implements(IGame)

    title = u"4x4 game"

    def __init__(self, context):
        self.context = context
