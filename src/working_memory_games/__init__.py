#-*- coding: utf-8 -*-
""" Pyramid startup """

from pyramid.config import Configurator

from working_memory_games.app import Application

import logging
logger = logging.getLogger("working_memory_games")


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
