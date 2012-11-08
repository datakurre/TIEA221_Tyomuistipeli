# -*- coding: utf-8 -*-
""" Interface definitions """

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """ Application, which is a dynamically instantiated transient object
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


class IPlayer(Interface):
    """ Player, which holds player's details and game sessions """

    name = Attribute("Player name")


class ISession(Interface):
    """ Session, which holds detailed gaming data """

    order = Attribute("Game play order during this session.")


class IGame(Interface):
    """ Game, which is a dynamically instantiated transient object """

    app = Attribute("Application object")

    session = Attribute("The current session")

    start_level = Attribute("Game start level")
    session_level = Attribute("The current level in the current session")

    def __init__(app):
        """ Game initialization requires an app """

    def set_session(session):
        """ Sets the current session for the game """
