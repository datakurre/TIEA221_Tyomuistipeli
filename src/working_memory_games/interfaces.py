# -*- coding: utf-8 -*-
""" Interface definitions """

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """ Application """

    player = Attribute("Current player")
    games = Attribute("Available games")


class IPlayer(Interface):
    """ Player """


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

    def get_new_game_items():
        """ Return a new set of items for the current level """
