#-*- coding: utf-8 -*-
""" Pyramid startup and URL dispatch / traversal registrations """

# XXX: Monkeypatch a bug in Pyramid 1.4a3 debug mode
import pyramid.config.predicates
pyramid.config.predicates.RequestMethodPredicate.__text__ = u"n/a"
pyramid.config.predicates.XHRPredicate.__text__ = u"n/a"
#

import os

import venusian

from pyramid.config import Configurator
from pyramid.response import FileResponse

from working_memory_games.app import Application
from working_memory_games.interfaces import IPlayer, IGame

import logging
logger = logging.getLogger("working_memory_games")


###
# Static file view factory
static_file = lambda filename: lambda request:\
    FileResponse(filename, request=request)
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
    """

    def __init__(self, **settings):
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, ob):
            name = name.lower()  # game id is its class name in lowercase
            config = context.config.with_package(info.module)

            # Register game so that sessions will be able to find it
            config.registry.registerAdapter(
                ob, name=name, required=(IPlayer,), provided=IGame)

            # Register main template for the game
            if settings.get("add_view", True):
                config.add_route(name, "/%s" % name, request_method="GET")
                config.add_view(route_name=name, renderer="%s.html" % name)

            # Register game specific static assets
            if settings.get("add_asset_views", True):
                dirname = os.path.join(
                    os.path.dirname(info.module.__file__), name)
                try:
                    resources = map(lambda x: os.path.join(dirname, x),
                                    os.listdir(dirname))
                except OSError:
                    resources = ()

                for path in filter(lambda x: os.path.isfile(x), resources):
                    basename = os.path.basename(path)
                    config.add_route(path, "/%s/%s" % (name, basename),
                                     request_method="GET")
                    config.add_view(static_file(path), route_name=path)

                for path in filter(lambda x: os.path.isdir(x), resources):
                    basename = os.path.basename(path)
                    config.add_static_view("%s/%s" % (name, basename),
                                           path=path)

        info = venusian.attach(wrapped, callback, category="pyramid")

        return wrapped


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application with routing """

    # Create Pyramid configurator
    config = Configurator(settings=settings)

    # Register robots.txt, humans.txt  and favicon.ico
    config.include("pyramid_assetviews")
    config.add_asset_views(
        "working_memory_games:",  # requires package name
        filenames=["robots.txt", "humans.txt", "favicon.ico"]
    )

    # Register Chameleon rendederer also for .html-files
    config.add_renderer(".html", "pyramid.chameleon_zpt.renderer_factory")

    # Enable ZODB support
    config.include("pyramid_zodbconn")
    config.include("pyramid_tm")

    # Configure common static resources
    config.add_static_view(name="bootstrap", path="bootstrap")
    config.add_static_view(name="static", path="static")

    # Configure common direct routes, which takes precedence over traverse
    config.add_route("root", "/")
    config.add_route("register", "/liity", request_method="GET")

    # Scan app views for their configuration
    config.scan(".app")

    # Scan games for their configuration
    config.scan(".games")

    # Configure traverse (for views that require access to the database)
    config.add_route("traversal", "/*traverse", factory=Application)

    # Make WSGI app
    return config.make_wsgi_app()
