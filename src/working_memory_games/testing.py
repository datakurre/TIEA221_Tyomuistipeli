# -*- coding: utf-8 -*-
"""Test layers for zope.testrunner"""

from plone.testing import Layer

from pyramid import testing

from pyramid.config import Configurator

from working_memory_games.app import Application


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application with mock database """
    # Configure
    config = Configurator(root_factory=lambda req: Application(req, {}),
                          settings=settings)

    # Register robots.txt and favicon.ico
    config.include("pyramid_assetviews")
    config.add_asset_views("working_memory_games:",  # requires package name
                           filenames=['robots.txt', 'favicon.ico'])

    # Note: No ZODB for testing!

    # Enable ZCML support
    config.include("pyramid_zcml")
    config.load_zcml("configure.zcml")

    # Enable imperative configuration for games
    config.scan(".games")

    # Make WSGI
    return config.make_wsgi_app()


class PyramidLayer(Layer):

    def setUp(self):
        self['config'] = testing.setUp(settings={})
        self['config'].include("pyramid_zcml")
        self['config'].include("configure_zcml")

    def tearDown(self):
        testing.tearDown()

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass

INTEGRATION_TESTING = PyramidLayer()


class PyramidServerLayer(Layer):

    def setUp(self):
        self['app'] = main({})

        # XXX: If the server needs a DB, set up test DB here.

        from wsgiref.simple_server import make_server
        self['server'] = make_server('', 55002, self['app'])
        self['server'].RequestHandlerClass.log_request =\
            lambda self, code, size: None  # mute http server

        from threading import Thread
        self['thread'] = Thread(target=self['server'].serve_forever)
        self['thread'].start()

    def tearDown(self):
        self['server'].shutdown()

        # XXX: If the server needs a DB, tear down test DB here.

        testing.tearDown()

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass

ACCEPTANCE_TESTING = PyramidServerLayer()


class Keywords(object):
    """Robot keywords"""

    def stop_for_debugging(self):
        import sys
        for attr in ('stdin', 'stdout', 'stderr'):
            setattr(sys, attr, getattr(sys, '__%s__' % attr))
        import pdb
        pdb.set_trace()
