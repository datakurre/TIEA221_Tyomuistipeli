# -*- coding: utf-8 -*-
import datetime
import logging
import random
import uuid
import math

from BTrees.Length import Length as LengthBase
from BTrees.IFBTree import intersection
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree as OOBTreeBase
from zope.interface import implements
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
from ZODB.utils import (
    u64,
    p64
)

from working_memory_games import interfaces


logger = logging.getLogger("working_memory_games")


class OOBTree(OOBTreeBase):
    """OOBTree, which can also hold direct persistent attributes and can be
    JSON-serialized

    """
    ###
    # Add persistent attribute support for OOBTree
    #
    # Loading attribute and mapping state in an OOBTree subclass by ZODB
    # requires custom __getstate__() and __setstate__() to handle load/save of
    # object state for both attributes and mapping keys/values (BTree buckets).
    # [wraps superclass __getstate__ and __setstate__ methods]
    #
    # http://pastie.org/1732745
    #
    def __getstate__(self):
        tree_state = super(OOBTree, self).__getstate__()
        attr_state = [(k, v) for k, v in self.__dict__.items()
                      if not (k.startswith('_v_') or k.startswith('__'))]
        return tree_state, attr_state

    def __setstate__(self, v):
        tree_state = v[0]
        attr_state = v[1]
        for k, v in attr_state:
            setattr(self, k, v)
        super(OOBTree, self).__setstate__(tree_state)
    ###

    def __json__(self, request):
        return dict(self.items())


class Length(LengthBase):
    """Generic integer based length, which handles conflict resolutions and can
    be JSON-serialized

    """
    def __json__(self, request):
        return self()


class ResultSet(object):
    """Iterable, which lazily maps catalog ids into real objects
    """

    def __init__(self, catalog, results):
        self.catalog = catalog
        self.results = results

    def __len__(self):
        return len(self.results)

    def __getitem__(self, item):
        if self._p_jar is None:
            self.catalog._v_jar.get(p64(self.results[item] + (2 ** 31)))
        else:
            self.catalog._p_jar.get(p64(self.results[item] + (2 ** 32)))


class Catalog(OOBTree):

    implements(interfaces.ICatalog)

    def index(self, obj, **kwargs):
        # When no ZODB, use volatile oids
        if self._p_jar is None:
            oid = obj._v_oid = getattr(obj, "_v_oid", None) \
                or p64(random.randint(0, 2 ** 31 - 1))
            self._v_jar = getattr(self, "_v_jar", None) or {}
            self._v_jar[obj._v_oid] = obj
        # Otherwise, use ZODB oids
        else:
            if obj._p_oid is None:
                self._p_jar.add(obj)
            oid = obj._p_oid
        # Index given values
        for key, value in kwargs.items():
            index = self.get(key, None)
            if index:
                # zope.index has limit of signed 32bit doc ids; to use the
                # full 32bit doc_id space, we start from (2 ** 31) * -1
                index.index_doc(u64(oid) - (2 ** 31), value)

    def query(self, **kwargs):
        indexes = filter(self.__contains__, kwargs.keys())
        results = (self[key].apply(value) for key, value in kwargs.items())
        return ResultSet(self, reduce(
            lambda x, y: intersection(x, y) if x and y else (), results))

    # Object class specific helpers:

    def index_player(self, player_id, player_obj):
        created = datetime.datetime.utcnow()  # just a default

        # Do a heuristic lookup for the creation datetime:
        if len(player_obj) > 0:
            first_session = player_obj[sorted(player_obj.keys())[0]]
            for game in first_session.values():
                for play in game.values():
                    if (play.get("start") or created) < created:
                        created = play.get("start")

        self.index(player_obj, **{
            "type": player_obj.__class__.__name__,
            "size": len(player_obj),
            "created": created,
            "player_obj_id": player_id,
            "keywords": filter(
                bool, [player_obj.details.get("assisted") and "assisted",
                       player_obj.details.get("registered") and "registered"]
            )
        })

        for session_obj in player_obj.values():
            self.index_session(player_id, session_obj)

    def index_session(self, player_id, session_obj):
        created = datetime.datetime.utcnow()  # just a default

        # Do a heuristic lookup for the creation datetime:
        if len(session_obj) > 0:
            for game in session_obj.values():
                for play in game.values():
                    if (play.get("start") or created) < created:
                        created = play.get("start")

        self.index(session_obj, **{
            "type": session_obj.__class__.__name__,
            "size": len(session_obj),
            "created": created,
            "player_id": player_id
        })

        for game_session_obj in session_obj.values():
            self.index_game_session(player_id, game_session_obj)

    def index_game_session(self, player_id, game_session_obj):
        created = datetime.datetime.utcnow()  # just a default

        # Do a heuristic lookup for the creation datetime:
        if len(game_session_obj) > 0:
            for play in game_session_obj.values():
                if (play.get("start") or created) < created:
                    created = play.get("start")

        self.index(game_session_obj, **{
            "type": game_session_obj.__class__.__name__,
            "size": len(game_session_obj),
            "created": created,
            "player_id": player_id,
        })


class Players(OOBTree):
    """Players container, which contains individual player data objects
    """

    implements(interfaces.IPlayers)

    def get_player(self, player_id):
        """Return player or None if player is not not found
        """
        return self.get(player_id)

    def create_player(self, name, details):
        """Creates a new Player
        """
        player_id = str(uuid.uuid4())
        self[player_id] = Player(name, details)
        return {
            'id': player_id
        }


class Player(OOBTree):
    """Player container, which holds details and game sessions for a single
    player

    """
    implements(interfaces.IPlayer)

    def __init__(self, name, details={}):
        super(Player, self).__init__()
        self.name = name
        self.details = PersistentMapping(details.items())

    @property
    def duration(self):
        total = datetime.timedelta(0)
        for session in self.values():
            total += getattr(session, "duration", datetime.timedelta(0))
        return total

    def session(self, games):
        """Create a new Session for today if needed. Always returns a session
        with games shuffled in random order.

        """
        today = str(datetime.datetime.utcnow().date())
        if not today in self:
            all_games = games.items()
            random.shuffle(all_games)
            selected_games = dict(all_games[:8])
            if self.details.get("assisted", False):
                self[today] = Session(selected_games, 0.30)
            else:
                self[today] = Session(selected_games)
        return self[today]

    def get_sessions(self):
        return map(lambda x: self[x], sorted(self.keys()))


class Session(OOBTree):
    """Session container, which holds daily gaming data for a single player for
    a single day

    """
    implements(interfaces.ISession)

    def __init__(self, games, assisted_cut=0):
        super(Session, self).__init__()
        game_items = games.items()

        # Kaikkien pelien kaikki pelikerrat yhteensä
        trials_total = sum(map(lambda game: game[1].day_limit, game_items))
        # Avustettavat pelit kaikista pelikerroista
        trials_assisted = int(math.ceil(trials_total * assisted_cut))

        # Avustettavissa olevat pelioliot
        assistable_games = filter(lambda game: game[1].can_assist, game_items)
        # Muut pelioliot
        normal_games = filter(lambda game: not game[1].can_assist, game_items)

        trials = []
        for name, game in assistable_games:
            for i in range(game.day_limit):
                trials.append({
                    "game": name,
                    "assisted": False
                })
        random.shuffle(trials)

        for i in range(min(trials_assisted, len(trials))):
            trials[i]["assisted"] = True

        for name, game in normal_games:
            for i in range(game.day_limit):
                trials.append({
                    "game": name,
                    "assisted": False
                })
        random.shuffle(trials)

        game_order = games.keys()
        random.shuffle(game_order)

        self.order = PersistentList(
            sorted(trials, cmp=lambda x, y, game_order=game_order:
                   cmp(game_order.index(x["game"]),
                       game_order.index(y["game"])))
        )

    @property
    def duration(self):
        total = datetime.timedelta(0)
        for game in self.values():
            total += getattr(game, "duration", datetime.timedelta(0))
        return total

    def get_game(self, name):
        if not name in self:
            self[name] = GameSession()
        return self[name]


class GameSession(OOBTree):
    """Game session container, which holds daily gaming data for a single
    player in a single game (for a single day)

    """
    implements(interfaces.IGameSession)

    def __init__(self):
        super(GameSession, self).__init__()
        self.duration = datetime.timedelta(0)
        #self.level = 3

    def get_plays(self):
        """Return all game plays (tries) of this game on today.
        """
        return map(self.__getitem__, sorted(self.keys()))

    def save_pass(self, gameinfo):
        time_key = str(datetime.datetime.utcnow())
        self[time_key] = gameinfo

    def save_fail(self, gameinfo):
        time_key = str(datetime.datetime.utcnow())
        self[time_key] = gameinfo
