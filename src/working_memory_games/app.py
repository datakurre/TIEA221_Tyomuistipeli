#-*- coding: utf-8 -*-
""" Main application, player management and session code """

import json
import random
import re
import urllib
import urlparse

from pyramid.view import (
    view_config,
    view_defaults
)

from pyramid.events import (
    BeforeRender,
    subscriber
)

from zope.interface import implements

from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPBadRequest

from pyramid_zodbconn import get_connection

from persistent.list import PersistentList

from working_memory_games.datatypes import (
    Players,
    Player
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

        # Migrate data over possible schema changes
        migrate(self.data)

        # Get registered games
        self.games = dict(self.request.registry.getAdapters((self,), IGame))

    def get_current_player(self):
        # Read cookie
        player_id = self.request.cookies.get("active_player")

        if player_id is None:
            raise HTTPFound(location=self.request.application_url + "/")

        # Look up the current player using the cookie data
        player = self.data.players.get(player_id)

        # Oops, player not found. Let's create one:
        if player is None:
            # Let's figure out, what players the browser knows
            default = urllib.quote(json.dumps([]))
            players = json.loads(urllib.unquote(
                self.request.cookies.get("players", default)
            ))
            players_by_id = dict(map(
                lambda x: (x.get('id'), x.get('name')),
                players
            ))
            if player_id in players_by_id:
                # Re-create named player with a name
                player = self.data.players[player_id] = Player(
                    players_by_id[player_id], {
                        "registered": True,
                        "assisted": self.get_assistance_flag()
                    }
                )
            else:
                # Or create just a guest
                player = self.data.players[player_id] = Player(
                    u"Guest", {
                        "registered": False,
                        "assisted": self.get_assistance_flag()
                    }
                )

        return player

    # def get_available_players(self):
    #     # Read cookies
    #     player_id = self.request.cookies.get("player_id")
    #     player_ids = self.request.cookies.get("player_ids", "").split(",")

    #     # Look up the available players using the cookie data
    #     players = dict([
    #         (x, self.data.players.get(x))
    #         for x in set([player_id] + player_ids)
    #         if x in self.data.players
    #     ])

    #     return players  # players may be an empty {}

    def get_current_session(self):
        """ Return the current (today's) session or creates a new one and
        returns it """

        player = self.get_current_player()

        if player is None:
            return None

        return player.session(self.games)

    def get_assistance_flag(self):
        """Return the next available value for assistance
        """
        if not hasattr(self.data, "assistance_flags"):
            self.data.assistance_flags = PersistentList()
        if len(self.data.assistance_flags) <= 0:
            self.data.assistance_flags.extend([True] * 5 + [False] * 5)
            random.shuffle(self.data.assistance_flags)
        return self.data.assistance_flags.pop(0)

    def __getitem__(self, name):
        """ Traverse to the given game """

        return self.games[name]  # raising a KeyError is allowed

    # @view_config(name="list_players", renderer="templates/list_players.html",
    #              request_method="GET", xhr=True)
    # def list_available_players(self):
    #     current_player = self.get_current_player()
    #     available_players = self.get_available_players()

    #     players = []
    #     counter = 0
    #     for player_id, player in available_players.items():
    #         css = "gameBtn btn-%s" % counter
    #         css += " selected" if player is current_player else ""
    #         players.append({
    #             "id": player_id,
    #             "name": player.name,
    #             "css": css
    #         })
    #         counter += 1

    #     cmp_by_name = lambda x, y: cmp(x["name"], y["name"])

    #     return {
    #         "players": sorted(players, cmp=cmp_by_name),
    #     }

    @view_config(name="liity", renderer="json",
                 request_method="POST")
    def create_new_player(self):
        name = self.request.params.get("name", "").strip()
        logging.debug(self.request.params)

        if not name:  # does not validate
            return HTTPBadRequest()

        details = {
            "registered": True,
            "assisted": self.get_assistance_flag()
        }
        details.update(self.request.params)
        return self.data.players.create_player(name, details)

    @view_config(name="kokeile", renderer="json",
                 request_method="POST")
    def create_new_guest(self):
        name = u"Guest"

        details = {
            "registered": False,
            "assisted": self.get_assistance_flag()
        }
        details.update(self.request.params)
        return self.data.players.create_player(name, details)

    @view_config(name="pelaa", renderer="templates/game_iframe.html",
                 request_method="GET", xhr=False)
    def get_next_game(self):

        session = self.get_current_session()

        if session is None:
            # User friendly version of:
            # raise HTTPBadRequest(u"No active session found.")
            raise HTTPFound(location=self.request.application_url + "/")

        if len(session.order) <= 0:
            # Daily session has ended
            raise HTTPFound(location=self.request.application_url
                            + "/#pelataan-taas-huomenna")

        print len(session.order)
        return {
            "game": session.order[0]["game"],
            "assisted": session.order[0]["assisted"]
        }

    @view_config(name="game_over", renderer="templates/game_over.html",
                 request_method="GET", xhr=False)
    def get_game_over(self):
		# TODO: calculate last game success.
        session = self.get_current_session()

        return {
            "game": session.order[0]["game"],
        }

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
    # Enforce that the application root is called with ending slash
    if not request.path.endswith("/"):
        url = urlparse.urljoin(request.application_url, request.path)
        raise HTTPFound(location=url + "/")
    return {}


@view_config(route_name="register", renderer="templates/register_player.html",
             request_method="GET")
def new_player_form(request):
    return {}
