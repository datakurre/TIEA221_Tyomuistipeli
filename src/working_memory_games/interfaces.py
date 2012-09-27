# -*- coding: utf-8 -*-
""" ZCA interface definitions """

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """ Application """

    player = Attribute("Current player")
    games = Attribute("Available games")


class IPlayer(Interface):
    """ Player """


class IGame(Interface):
    """ Game """

    title = Attribute("Game title")
    player = Attribute("Current player")

    __name__ = Attribute("Dynamically set game lookup name")

    def __init__(player):
        """ Game initialization requires a player object """
