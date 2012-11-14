# -*- coding: utf-8 -*-
""" Interface definitions """

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """ Application is a dynamically instantiated transient controller object
    with pointers to real persistent data """

    request = Attribute("Current request")

    data = Attribute("Database root")
    games = Attribute("Available games")

    def get_current_player():
        """ Return the current player (or guest) """

    def get_current_session():
        """ Return the current session for the current player """

    def get_available_players():
        """ Return a dict of available players for the current browser session
        """


class IGame(Interface):
    """ Game is a dynamically instantiated transient controller object for a
    single game with pointers to real persistent data """

    app = Attribute("Application object")

    start_level = Attribute("Game start level")

    session = Attribute("The current session")

    def __init__(app):
        """ Game initialization requires an app """


class IPlayers(Interface):
    """ Players container, which contains individual player data objects """


class IPlayer(Interface):
    """ Player container, which holds details and game sessions for a single
    player """

    name = Attribute("Player name")


class ISession(Interface):
    """ Session container, which holds daily gaming data for a single player
    for a single day """

    order = Attribute("Game play order during this session.")


class IGameSession(Interface):
    """ Game session container, which holds daily gaming data for a single
    player in a single game (for a single day) """
