# -*- coding: utf-8 -*-
""" Interface definitions """

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """ Application, which is a dynamically instantiated transient object
    with pointer to real persistent data """

    root = Attribute("Database root object")

    player = Attribute("Current player. Player can be registered or a guest.")
    players = Attribute("Available players (for the current browser session)")

    games = Attribute("Available games")


class IPlayer(Interface):
    """ Player, which holds player's details and game sessions """

    name = Attribute("Player name")


class ISession(Interface):
    """ Session, which holds detailed gaming data """


class IGame(Interface):
    """ Game, which is a dynamically instantiated transient object """

    name = Attribute("Game id")
    title = Attribute("Game title")

    start_level = Attribute("Game start level")

    session = Attribute("The current session")
    session_data = Attribute("Game data for the current session")
    session_level = Attribute("The current level in the current session")

    def __init__(session):
        """ Game initialization requires a session object """
