# -*- coding: utf-8 -*-
""" Interface definitions """

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """ Application """

    root = Attribute("Database root object")

    player = Attribute("Current player")
    players = Attribute("Available players (for the current session)")

    games = Attribute("Available games")


class IPlayer(Interface):
    """ Player """

    name = Attribute("Player name")


class IGame(Interface):
    """ Game """

    name = Attribute("Game id")
    title = Attribute("Game title")

    start_level = Attribute("Game start level")

    player = Attribute("The current player")
    player_data = Attribute("Game data for the current player")
    player_level = Attribute("The current level of the current player")

    def __init__(player):
        """ Game initialization requires a player object """
