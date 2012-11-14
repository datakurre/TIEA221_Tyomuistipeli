# -*- coding: utf-8 -*-
""" Migration steps for database model upgrades """

CURRENT_VERSION = 3  # simply an incrementing integer value

import logging
logger = logging.getLogger("working_memory_games")


def migrate(data):
    from working_memory_games import upgrades as steps

    data_version = getattr(data, "version", 0)

    for version in range(data_version, CURRENT_VERSION):
        logger.info("Migrating database from version %s to %s.",
                    version, version + 1)
        getattr(steps, "from%sto%s" % (version, version + 1))(data)
        setattr(data, "version", version + 1)


def from0to1(data):
    """ Moves main containers from key-values into attributes """

    if "players" in data:
        data.players = data["players"]
        del data["players"]

    if "guests" in data:
        data.guests = data["guests"]
        del data["guests"]


def from1to2(data):
    """ Delete pre-session gaming data """

    from working_memory_games.interfaces import ISession

    for player_id in data.players:
        player = data.players[player_id]
        for session_id in player:
            session = player[session_id]
            if not ISession.providedBy(session):
                del data.players[player_id][session_id]  # Sorry!


def from2to3(data):
    """ Re-base generic OOBTree-types to custom types to make it easier to add
    supportive methods for them """

    from working_memory_games.datatypes import (
        Players,
        GameSession
    )

    if not isinstance(data.players, Players):
        data.players.__class__ = Players
        data.players._p_changed = True  # force to commit the class change

    if not isinstance(data.guests, Players):
        data.guests.__class__ = Players
        data.guests._p_changed = True  # force to commit the class change

    for player_id in data.players:
        player = data.players[player_id]
        for session_id in player:
            session = player[session_id]
            for game_id in session:
                game_session = session[game_id]
                game_session.__class__ = GameSession
                game_session._p_changed = True
                session._p_changed = True

    for player_id in data.guests:
        player = data.players[player_id]
        for session_id in player:
            session = player[session_id]
            for game_id in session:
                game_session = session[game_id]
                game_session.__class__ = GameSession
                game_session._p_changed = True
                session._p_changed = True
