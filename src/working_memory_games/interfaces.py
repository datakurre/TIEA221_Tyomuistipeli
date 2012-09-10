# -*- coding: utf-8 -*-
""" ZCA interface definitions """

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """ Marker interface for the application root object """


class IGame(Interface):
    """ Marker interface for a game object """

    title = Attribute("Game title")
