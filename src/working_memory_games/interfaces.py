# -*- coding: utf-8 -*-
"""Interface definitions for adapter registrations and object introspection
"""

from zope.interface import Interface, Attribute


class IApplication(Interface):
    """Application is a dynamically instantiated transient controller object
    with pointers to real persistent data

    """
    request = Attribute("Current request")

    data = Attribute("Database root")
    games = Attribute("Available games")

    def get_current_player():
        """Return the current player (or guest)
        """

    def get_current_session():
        """Return the current session for the current player
        """

    def get_available_players():
        """Return a dict of available players for the current browser session
        """


class ICatalog(Interface):
    """Catalog is a BTree of indexes with object to id mapping

    """
    objects = Attribute("BTree of all indexed objects by their index ids")
    ids = Attribute("BTree of all index ids by their objects")

    def index(obj, **kwargs):
        """Indexes object with given values
        """

    def query(**kwargs):
        """Returns lazy query result sets for the given query arguments
        """


class IGame(Interface):
    """Game is a dynamically instantiated transient controller object for a
    single game with pointers to real persistent data

    """
    start_level = Attribute("Game start level")

    app = Attribute("Application object")
    player = Attribute("The current player")
    session = Attribute("The current session")

    def __init__(app):
        """Game initialization requires an app
        """

    def get_last_levels(self, n=None, pass_only=False):
        """Return last n levels for the game for the current player
        in reverse chronological order

        """

class IPlayers(Interface):
    """Players container, which contains individual player data objects
    """


class IPlayer(Interface):
    """Player container, which holds details and game sessions for a single
    player

    """
    name = Attribute("Player name")
    duration = Attribute("Total game play during all sessions.")


class ISession(Interface):
    """Session container, which holds daily gaming data for a single player
    for a single day

    """
    order = Attribute("Game play order during this session.")
    duration = Attribute("Total game play time during this session.")


class IGameSession(Interface):
    """Game session container, which holds daily gaming data for a single
    player in a single game (for a single day)

    """
    last_start = Attribute("Last datetime on when a new game has been started")
    duration = Attribute("Datetime delta on how much the game has been "
                         "played during today's game session.")
