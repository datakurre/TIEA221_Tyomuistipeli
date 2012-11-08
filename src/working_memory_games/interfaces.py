# -*- coding: utf-8 -*-
""" Interface definitions """

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """ Application, which is a dynamically instantiated transient object
    with pointers to real persistent data """

    request = Attribute("Active request")
    root = Attribute("Database root")

    def get_current_player():
        """ Return the current player (or guest) """

    def get_available_players():
        """ Return a dict of available players for the current browser session
        """

    def get_available_games():
        """ Return a dict of available games """

    def get_current_session():
        """ Return the current session for the current player """


class IPlayer(Interface):
    """ Player, which holds player's details and game sessions """

    name = Attribute("Player name")


class ISession(Interface):
    """ Session, which holds detailed gaming data """

    order = Attribute("Game play order during this session.")


class IGame(Interface):
    """ Game, which is a dynamically instantiated transient object """

    app = Attribute("Application object")

    start_level = Attribute("Game start level")

    session = Attribute("The current session")
    session_data = Attribute("Game data for the current session")
    session_level = Attribute("The current level in the current session")

    def __init__(session):
        """ Game initialization requires a session object """
