# -*- coding: utf-8 -*-
""" Pyramid application initialization and startup functions """

from zope.interface import implements

from pyramid.config import Configurator

from pyramid_zodbconn import get_connection

from working_memory_games.interfaces import (
    IApplication,
    IGame
)


class Application(object):
    """ This function returns the application root object (with ZODB) """
    implements(IApplication)

    def __init__(self, request):
        self.context = get_connection(request).root()
        self.request = request

    def __getitem__(self, key):
        registry = self.request.registry
        games = dict(registry.getAdapters((self,), IGame))
        return games.get(key, self.context[key])


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application """
    # Configure
    config = Configurator(root_factory=Application,
                          settings=settings)

    # Enable ZODB support
    config.include("pyramid_zodbconn")
    config.include("pyramid_tm")

    # Enable ZCML support
    config.include("pyramid_zcml")
    config.load_zcml("configure.zcml")

    # Make WSGI
    return config.make_wsgi_app()
