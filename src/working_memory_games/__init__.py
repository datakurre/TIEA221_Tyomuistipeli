#-*- coding: utf-8 -*-
""" Pyramid startup """

import venusian

from pyramid.config import Configurator

from working_memory_games.app import Application
from working_memory_games.interfaces import IPlayer, IGame

import logging
logger = logging.getLogger("working_memory_games")


class game_config(object):
    """ A class decorator which allows a developer to config game registrations
    nearer to actual code. """

    def __init__(self, **settings):
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, ob):
            config = context.config.with_package(info.module)

            # Register game
            config.registry.registerAdapter(ob, name=ob.name,
                                            required=(IPlayer,),
                                            provided=IGame)

            if settings.get("add_view", True):
                config.add_view(context=ob, renderer="%s.html" % ob.name)

            if settings.get("add_static_view", True):
                config.add_static_view("%s/static" % ob.name, path=ob.name)

        info = venusian.attach(wrapped, callback, category="pyramid")

        return wrapped


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application """
    # Configure
    config = Configurator(root_factory=Application, settings=settings)

    # Register robots.txt and favicon.ico
    config.include("pyramid_assetviews")
    config.add_asset_views("working_memory_games:",  # requires package name
                           filenames=["robots.txt", "favicon.ico"])

    # Register Chameleon rendederer also for .html-files
    config.add_renderer(".html", "pyramid.chameleon_zpt.renderer_factory")

    # Enable ZODB support
    config.include("pyramid_zodbconn")
    config.include("pyramid_tm")

    # Configure static resources
    config.add_static_view(name="bootstrap", path="bootstrap")
    config.add_static_view(name="static", path="static")

    # Configure app
    config.scan(".app")

    # Configure games
    config.scan(".games")

    # Make WSGI
    return config.make_wsgi_app()
