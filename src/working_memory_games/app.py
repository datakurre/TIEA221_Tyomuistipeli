#-*- coding: utf-8 -*-
"""Main application, player management and session code
"""

import json
import random
import re
import urllib
import urlparse
import datetime

from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.events import (
    BeforeRender,
    subscriber
)

from zope.interface import implements
from zope.index.field import FieldIndex
from zope.index.keyword import KeywordIndex

from pyramid.renderers import get_renderer
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPBadRequest
)

from pyramid_zodbconn import get_connection

from persistent.list import PersistentList

from working_memory_games.datatypes import (
    Catalog,
    Players,
    Player
)

from working_memory_games.upgrades import migrate
from working_memory_games.interfaces import (
    IApplication,
    IGame,
)
from working_memory_games.logger import logger


@view_defaults(context=IApplication, route_name="traversal")
class Application(object):
    """Dynamic application root object, which provides access to the
    database and enables path traverse for available games

    """
    implements(IApplication)

    def __init__(self, context, request=None):
        """Initialize application for each request
        """
        # Support initialization as a view class instance
        if issubclass(context.__class__, self.__class__):
            self.__dict__.update(context.__dict__)
            return

        # Continue initialization as a root object instance
        self.data = request  # 'request' is either None or a mockup db like {}
        self.request = context  # 'context' is the request for root_factory

        # Get database root from ZODB when no mockup db was given
        if self.data is None:
            self.data = get_connection(self.request).root()

        # Prepare database
        if not hasattr(self.data, "players"):
            self.data.players = Players()
        if not hasattr(self.data, "catalog"):
            self.data.catalog = Catalog()
            self.data.catalog["type"] = FieldIndex()
            self.data.catalog["size"] = FieldIndex()
            self.data.catalog["created"] = FieldIndex()
            self.data.catalog["player_id"] = FieldIndex()
            self.data.catalog["keywords"] = KeywordIndex()

        # Migrate data over possible schema changes
        migrate(self.data)

        # Set registered games (available games could be filtered here)
        self.games = dict(self.request.registry.getAdapters((self,), IGame))
        # E.g. self.games = {"numbers": self.games["numbers"]}

    def get_current_player(self, player_id=''):
        """Return the current player according to the available cookie data
        """
        # Read cookie
        if player_id == '':
            player_id = self.request.cookies.get("active_player")

        # When player_id was not available, redirect to application root
        if player_id is None:
            logger.debug('player id is None')
            raise HTTPFound(location=self.request.application_url + "/")

        # Look up the current player using the cookie data
        player = self.data.players.get(player_id)

        # When player was not found, create one for convenience
        if player is None:

            # Figure out, what players the browser knows
            default = urllib.quote(json.dumps([]))
            players = json.loads(urllib.unquote(
                self.request.cookies.get("players", default)
            ))
            players_by_id = dict([(player.get('id'), player.get('name'))
                                  for player in players])
            if player_id in players_by_id:
                # Re-create named player with the given name
                player = self.data.players[player_id] = Player(
                    players_by_id[player_id], {
                        "registered": True,
                        "assisted": self.get_next_assistance_flag()
                    }
                )
            else:
                # Or create an incognito guest player
                player = self.data.players[player_id] = Player(
                    u"Guest", {
                        "registered": False,
                        "assisted": self.get_next_assistance_flag()
                    }
                )
            self.data.catalog.index_player(player_id, player)

        return player

    def get_current_session(self, player_id=''):
        """Return the current (today's) session or create a new one and
        return it

        """
        player = self.get_current_player(player_id)
        if player is not None:
            session = player.session(self.games)
            if len(session) == 0:
                self.data.catalog.index_session(player_id, session)
            return session
        else:
            return None

    def get_next_assistance_flag(self):
        """Return the next available value for assistance
        """
        if not hasattr(self.data, "assistance_flags"):
            self.data.assistance_flags = PersistentList()
        if len(self.data.assistance_flags) <= 0:
            self.data.assistance_flags.extend([True] * 5 + [False] * 5)
            random.shuffle(self.data.assistance_flags)
        return self.data.assistance_flags.pop(0)

    def __getitem__(self, name):
        """Traverse to the given game
        """
        return self.games[name]  # raising a KeyError is allowed

    @view_config(name="liity", renderer="json",
                 request_method="POST", http_cache=0)
    def create_new_player(self):
        """Save named player information
        """
        name = self.request.params.get("name", "").strip()
        logger.debug(self.request.params)

        if not name:  # does not validate
            return HTTPBadRequest()

        details = {
            "registered": True,
            "assisted": self.get_next_assistance_flag()
        }
        details.update(self.request.params)

        data = self.data.players.create_player(name, details)
        player = self.data.players[data["id"]]
        self.data.catalog.index_player(data["id"], player)
        return data

    @view_config(name="pelinappulat", renderer="json",
                 request_method="POST", http_cache=0)
    def send_email(self):
        """Save named player information
        """
        email = self.request.params.get("email", "").strip()
        logger.debug(self.request.params)

        if not email:  # does not validate
            return HTTPBadRequest()

        players = []
        for playerid, player in self.data.players.items():
            if 'email' in player.details and player.details['email'] == email:
                #print 'send player id to ', player.details['email'], playerid, player.details
                players.append({ 'name': player.details['name'] or '',
                                 'id': playerid
                                 })
        if len(players) > 0:
            logger.info('Send players for email: '+email)
            import emailer
            emailer.email(email, players)
        else:
            logger.info('No players for email: '+email)
        return {}


    @view_config(name="kokeile", renderer="json",
                 request_method="POST", http_cache=0)
    def create_new_guest(self):
        """Save new guest
        """
        name = u"Guest"

        details = {
            "registered": False,
            "assisted": self.get_next_assistance_flag()
        }
        details.update(self.request.params)

        data = self.data.players.create_player(name, details)
        player = self.data.players[data["id"]]
        self.data.catalog.index_player(data["id"], player)
        return data

    @view_config(name="next_game", renderer="json", http_cache=0)
    def get_next_game(self):
        """Return the next available game for the current player
        """
        session = self.get_current_session()

        # TODO: Refactor these into BadRequests and reflect that refactoring
        # into game_iframe.js code
        if session is None:
            logger.debug('session length is None')
            # User friendly version of:
            # raise HTTPBadRequest(u"No active session found.")
            raise HTTPFound(location=self.request.application_url + "/")

        # Check the possible broken game and skip it. A broken game is a game
        # that has been started at least once before during the session, but is
        # never completed during the session and more than 10 seconds have
        # elapsed since the last start.
        if len(session.order) > 0:
            datetime_now = datetime.datetime.utcnow()
            next_game = session.order[0]['game']
            next_game_is_broken = (
                next_game in session
                and len(session[next_game]) == 0
                and (datetime_now
                     - getattr(session[next_game], 'last_start', datetime_now)
                     > datetime.timedelta((1.0 / 24 / 60 / 60) * 10))  # > 10s
            )
            if next_game_is_broken:
                logger.warn("Removing game '{0:s}' from session.order.".format(
                    next_game))
                next_game_is_in = lambda order:\
                    len(order) > 0 and order[0]['game'] == next_game
                while next_game_is_in(session.order):
                    session.order.pop(0)
                # Do explicit commit, because HTTPFound later would rollback
                if len(session.order) >= 0:
                    import transaction
                    transaction.commit()

        if len(session.order) <= 0:
            logger.debug('session length is 0')
            # Daily session has ended
            raise HTTPFound(location=self.request.application_url
                            + "/#pelataan-taas-huomenna")

        logger.debug("Games left in session: '{0:s}'.".format(session.order))

        return {
            "game": session.order[0]["game"],
            "assisted": session.order[0]["assisted"]
        }

    @view_config(name="session_status", renderer="json", http_cache=0)
    def get_session_statuses_for_today(self):
        ret = {}
        players_json = self.request.cookies.get("players")
        if players_json is not None:
            players = json.loads(urllib.unquote(players_json))
            for player in players:
                player_id = player.get("id")
                if player_id is not None:
                    session = self.get_current_session(player_id)
                    ret[player_id] = {"session_over": len(session.order) == 0}
        return ret


@subscriber(BeforeRender)
def add_base_template(event):
    """Define base template and available globals for Chameleon renderer
    """
    base_template =\
        get_renderer("templates/base_template.html").implementation()

    request = event["request"]
    base_url = request.application_url
    current_url = urlparse.urljoin(request.application_url, request.path)

    event.update({
        "base_template": base_template,
        "base_url": re.sub("/$", "", base_url),
        "current_url": re.sub("/$", "", current_url),
        # ^^ We always strip the ending slash so that we can always use these
        # variables like ${base_url}/something without ending up with double
        # slashes in URLs.
        "current_url_encoded": urllib.urlencode({
            "u": re.sub("/$", "", current_url)
        })[2:],
    })


@view_config(route_name="root", renderer="templates/index.html",
             http_cache=(datetime.timedelta(1), {"public": True}))
def root_view(request):
    """Static main menu view
    """
    # Enforce that the application root is always called with ending slash
    if not request.path.endswith("/"):
        url = urlparse.urljoin(request.application_url, request.path)
        raise HTTPFound(location=url + "/")
    return {}


@view_config(route_name="play", renderer="templates/game_iframe.html",
             http_cache=(datetime.timedelta(1), {"public": True}))
def game_iframe_view(request):
    assert request  # please pyflakes
    return {}
