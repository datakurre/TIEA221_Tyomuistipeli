# -*- coding: utf-8 -*class definitions-
"""ZODB persistent resource class definitions"""

from persistent.mapping import PersistentMapping

from zope.interface import implements

from kog_working_mem.interfaces import (
    IApplication,
    IContainer
)


class Container(PersistentMapping):
    """Generic container"""
    implements(IContainer)


class Application(Container):
    """Application root container"""
    implements(IApplication)

    __name__ = None
    __parent__ = None
