# -*- coding: utf-8 -*-
"""Pyramid application initialization and startup functions"""

from zope.interface import alsoProvides

from pyramid.config import Configurator

from pyramid_zodbconn import get_connection

from kog_working_mem.interfaces import IApplication


def root_factory(request):
    """This function returns the application root object (from ZODB)"""
    # Connect and retrieve ZODB root
    conn = get_connection(request)
    zodb_root = conn.root()
    alsoProvides(zodb_root, IApplication)
    return zodb_root


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application"""
    # Configure
    config = Configurator(root_factory=root_factory,
                          settings=settings)

    # Enable ZODB support
    config.include("pyramid_zodbconn")
    config.include("pyramid_tm")

    # Enable ZCML support
    config.include("pyramid_zcml")
    config.load_zcml("configure.zcml")

    # Make WSGI
    return config.make_wsgi_app()
