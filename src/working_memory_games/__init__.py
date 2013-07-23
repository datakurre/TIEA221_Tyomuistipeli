#-*- coding: utf-8 -*-
"""Pyramid startup and URL dispatch / traversal registrations
"""

# XXX: Monkeypatch a bug in Pyramid 1.4a3 debug mode
import pyramid.config.predicates
pyramid.config.predicates.RequestMethodPredicate.__text__ = u"n/a"
pyramid.config.predicates.XHRPredicate.__text__ = u"n/a"
#

import os
import datetime

import venusian

from pyramid.config import Configurator
from pyramid.response import FileResponse
from pyramid.renderers import JSON
from pyramid.httpexceptions import HTTPNotFound

from working_memory_games.app import Application

from working_memory_games.interfaces import (
    IApplication,
    IGame
)

import logging
logger = logging.getLogger("working_memory_games")


###
# Static file view factory
static_file = lambda filename: lambda request:\
    FileResponse(filename, request=request)
###

###
# JSON adapter with support for datetime.timedelta and numpy.int
json_renderer = JSON()

def datetime_timedelta_adapter(obj, request):
    return float(obj.total_seconds())
json_renderer.add_adapter(datetime.timedelta, datetime_timedelta_adapter)

def int_adapter(obj, request):
    return int(obj)
json_renderer.add_adapter(int, int_adapter)
###


class game_config(object):
    """ A class decorator which allows a developer to configure game related
    registrations nearer to actual code.

    This decorator will provide magic to register all necessary stuff for
    a single game, whatever it ends to be.

    Currently this decorater accepts two parameters:

    add_view
        which accepts a boolean value and triggers registering the game
        template at ``/gamename``

    add_asset_views
        which accepts a boolean value and triggers registering the game
        related static resource directory at  ``/gamename/static``

    The decorator also registers some view defaults for the possible
    view methods within the class:

    context
        the current game
    route_name
        traversal
    renderer
        json
    xhr
        True

    Please, note that it's not possible to use Pyramid's @view_defaults
    together with @game_config (the latest one in chain will prevail).
    """

    def __init__(self, **settings):
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        ##
        # Register view method defaults for the game class
        wrapped.__view_defaults__ = {
            "context": wrapped,
            "route_name": "traversal",
            "renderer": "json"
        }
        ##

        def callback(context, name, ob):
            name = name.lower()  # game id is its class name in lowercase
            config = context.config.with_package(info.module)

            logging.info("Registering game '%s'." % name)

            # Register game so that sessions will be able to find it
            config.registry.registerAdapter(
                ob, name=name, required=(IApplication,), provided=IGame)

            # Register main template for the game
            if settings.get("add_view", True):
                config.add_route(name, "/%s/" % name, request_method="GET")
                config.add_view(route_name=name, renderer="%s.html" % name)

            # Register game specific static assets
            if settings.get("add_asset_views", True):
                dirname = os.path.dirname(info.module.__file__)
                try:
                    resources = map(lambda x: os.path.join(dirname, x),
                                    os.listdir(dirname))
                except OSError:
                    resources = ()

                for path in filter(lambda x: os.path.isfile(x), resources):
                    basename = os.path.basename(path)
                    config.add_route(path, "/%s/%s" % (name, basename),
                                     request_method="GET")
                    if path.endswith('.js') or path.endswith('.css'):
                        #print 'register', path
                        config.add_view(route_name=path, view=static_file(path), http_cache=3600)
                    else:
                        config.add_view(route_name=path, view=static_file(path))
                for path in filter(lambda x: os.path.isdir(x), resources):
                    #print 'static register', path
                    basename = os.path.basename(path)
                    config.add_static_view("%s/%s" % (name, basename),
                                           path=path, cache_max_age=3600)

        info = venusian.attach(wrapped, callback, category="pyramid")

        return wrapped


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application with routing
    """
    # Create Pyramid configurator
    config = Configurator(settings=settings)

    # Auto append ending slash when not found would turn to found with it
    config.add_notfound_view(lambda request: HTTPNotFound(), append_slash=True)

    # Register robots.txt, humans.txt  and favicon.ico
    for filename in ["robots.txt", "humans.txt", "favicon.ico",
                     "tutkimussuunnitelma.pdf"]:
        path = os.path.join(os.path.dirname(__file__), filename)
        config.add_route(path, "/%s" % filename)
        config.add_view(route_name=path, view=static_file(path), http_cache=3600)

    # Configure common static resources
    config.add_static_view(name="css", path="css", cache_max_age=3600)
    config.add_static_view(name="img", path="img", cache_max_age=3600)
    config.add_static_view(name="snd", path="snd", cache_max_age=3600)
    config.add_static_view(name="js", path="js", cache_max_age=3600)
    config.add_static_view(name="lib", path="lib", cache_max_age=3600)

    # Register Chameleon renderer also for .html-files
    config.add_renderer(".html", "pyramid.chameleon_zpt.renderer_factory")

    # Configure common direct routes, which takes precedence over traverse
    config.add_route("root", "/")
    config.add_route("register", "/liity", request_method="GET")

    # Scan app views for their configuration
    config.scan(".app")

    # Scan games for their configuration
    config.scan(".games")

    # Enable ZODB support
    config.include("pyramid_zodbconn")
    config.include("pyramid_tm")

    # Configure traverse (for views that require access to the database)
    config.add_route("traversal", "/*traverse", factory=Application)

    # Register custom JSON renderer with timedelta adapter
    config.add_renderer("json", json_renderer)

    # Make WSGI app
    return config.make_wsgi_app()
