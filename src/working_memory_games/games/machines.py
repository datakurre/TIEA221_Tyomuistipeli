# -*- coding: utf-8 -*-
""" Machines """

from zope.interface import implements

from working_memory_games.interfaces import IGame
from working_memory_games.games import Game


class Machines(Game):
    """ Machines """

    implements(IGame)

    name = "machines"
    title = u"Koneita"
