# -*- coding: utf-8 -*-
""" Persistent types """

from zope.interface import implements

from BTrees.OOBTree import OOBTree as OOBTreeBase
from BTrees.Length import Length as LengthBase

from working_memory_games.interfaces import IPlayer

import logging
logger = logging.getLogger("working_memory_games")


class OOBTree(OOBTreeBase):
    """ JSON-serializable OOBTree """

    def __json__(self, request):
        return dict(self.items())

class Length(LengthBase):
    """ JSON-serializable Length (a numeric value with conflict resolution) """

    def __json__(self, request):
        return str(self())


class Player(OOBTree):
    """ Player """

    implements(IPlayer)