#-*- coding: utf-8 -*-
""" Main application, player management and session code """

import re
import uuid
import datetime
import urlparse
import random

from pyramid.view import (
    view_config,
    view_defaults
)

from pyramid.events import (
    BeforeRender,
    subscriber
)

from zope.interface import implements

from webob.headers import ResponseHeaders

from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound

from pyramid_zodbconn import get_connection

from working_memory_games.datatypes import (
    Players,
    Player,
    Session
)

from working_memory_games.upgrades import migrate

from working_memory_games.interfaces import (
    IApplication,
    IGame,
)

import logging
logger = logging.getLogger("working_memory_games")


@view_defaults(context=IApplication, route_name="traversal")
class Application(object):
    """ Dynamic application root object, which provides access to the
    database and enables traverse for available games """

    implements(IApplication)

    def __init__(self, context, request=None):

        # Support initialization as a view class instance
        if issubclass(context.__class__, self.__class__):
            self.__dict__.update(context.__dict__)
            return

        # Continue initialization as a root object instance
        self.data = request  # 'request' is either None or a mock up db like {}
        self.request = context  # 'context' is the request for root_factory

        # Get database root from ZODB
        if self.data is None:
            self.data = get_connection(self.request).root()

        # Prepare database
        if not hasattr(self.data, "players"):
            self.data.players = Players()

        if not hasattr(self.data, "guests"):
            # XXX: Eventually, guests should be stored into temporary database,
            # which would be cleaned when the server is restarted.  I'll fix
            # this, once I figure out the proper ZEO-configuration... -Asko
            self.data.guests = Players()

        # Migrate data over possible schema changes
        migrate(self.data)

        # Get registered games
        self.games = dict(self.request.registry.getAdapters((self,), IGame))

    def get_current_player(self):
        # Read cookie
        player_id = self.request.cookies.get("player_id")

        # Look up the current player using the cookie data
        player = self.data.players.get(player_id)

        # When player is not found, try to look up a guest
        if player is None:
            player = self.data.guests.get(player_id)

        return player  # player may be None

    def get_available_players(self):
        # Read cookies
        player_id = self.request.cookies.get("player_id")
        player_ids = self.request.cookies.get("player_ids", "").split(",")

        # Look up the available players using the cookie data
        players = dict([
            (x, self.data.players.get(x))
            for x in set([player_id] + player_ids)
            if x in self.data.players
        ])

        # Do implicit cookie-refresh
        if players:
            self.request.response.set_cookie(
                "player_ids", ",".join(players.keys()),
                max_age=(60 * 60 * 24 * 365)
            )

        return players  # players may be an empty {}

    def get_current_session(self):
        """ Return the current (today's) session or creates a new one and
        returns it """

        player = self.get_current_player()

        if player is None:
            return None

        today = str(datetime.datetime.utcnow().date())
        session = player.get(today)

        if session is None:
            session = player[today] = Session()

        if not hasattr(session, "order"):
            session.order = self.games.keys()
            random.shuffle(session.order)

        return session

    def __getitem__(self, name):
        """ Traverse to the given game """

        return self.games[name]  # raising a KeyError is allowed

    @view_config(name="list_players", renderer="templates/list_players.html",
                 request_method="GET", xhr=True)
    def list_available_players(self):
        current_player = self.get_current_player()
        available_players = self.get_available_players()

        players = []
        counter = 0
        for player_id, player in available_players.items():
            css = "gameBtn btn-%s" % counter
            css += " selected" if player is current_player else ""
            players.append({
                "id": player_id,
                "name": player.name,
                "css": css
            })
            counter += 1

        cmp_by_name = lambda x, y: cmp(x["name"], y["name"])

        return {
            "players": sorted(players, cmp=cmp_by_name),
        }

    @view_config(name="liity", renderer="templates/register_player.html",
                 request_method="POST", xhr=False)
    def create_new_player(self):
        name = self.request.params.get("name", "").strip()
        logging.debug(self.request.params)

        if not name:  # does not validate
            return self.request.params

        player_id = str(uuid.uuid4())

        self.data.players[player_id] = Player(name=name)
        self.request.response.set_cookie(
            "player_id", player_id,
            max_age=(60 * 60 * 24 * 365)
        )
        headers = ResponseHeaders({
            "Set-Cookie": self.request.response.headers.get("Set-Cookie")
        })

        return HTTPFound(location=self.request.application_url,
                         headers=headers)

    @view_config(name="select_player",
                 request_method="POST", xhr=False)
    def select_player(self):

        player_id = self.request.params.get("player_id", "").strip()

        if not player_id in self.data.players:
            return self.request.params

        self.request.response.set_cookie(
            "player_id", player_id,
            max_age=(60 * 60 * 24 * 365)
        )
        headers = ResponseHeaders({
            "Set-Cookie": self.request.response.headers.get("Set-Cookie")
        })

        return HTTPFound(location=self.request.application_url,
                         headers=headers)


    @view_config(name="select_guest",
                 request_method="POST", xhr=False)
    def select_guest(self):

        player_id = str(uuid.uuid4())
        self.data.guests[player_id] = Player(name=u"Guest")

        self.request.response.set_cookie(
            "player_id", player_id,
            max_age=(60 * 60 * 24 * 365)
        )
        headers = ResponseHeaders({
            "Set-Cookie": self.request.response.headers.get("Set-Cookie")
        })

        return HTTPFound(location=self.request.application_url,
                         headers=headers)

    @view_config(name="dump", renderer="json", xhr=False)
    def dump_saved_data(self):
        return dict(self.get_current_player().items())


@subscriber(BeforeRender)
def add_base_template(event):
    """ Adds base template for Chameleon renderer """

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
    })


@view_config(route_name="root", renderer="templates/index.html")
def root_view(request):
    return {}


@view_config(route_name="register", renderer="templates/register_player.html",
             request_method="GET")
def new_player_form(request):
    return {}
