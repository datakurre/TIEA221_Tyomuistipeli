# -*- coding: utf-8 -*-
""" Test layers for zope.testrunner """

import os

from plone.testing import Layer

from pyramid import testing

from pyramid.config import Configurator

from working_memory_games import static_file
from working_memory_games.app import Application


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application with mock database """

    # Create Pyramid configurator
    config = Configurator(settings=settings)

    # Register robots.txt, humans.txt  and favicon.ico
    for filename in ["robots.txt", "humans.txt", "favicon.ico"]:
        path = os.path.join(os.path.dirname(__file__), filename)
        config.add_route(path, "/%s" % filename)
        config.add_view(route_name=path, view=static_file(path))

    # Configure common static resources
    config.add_static_view(name="css", path="css")
    config.add_static_view(name="img", path="img")
    config.add_static_view(name="js", path="js")
    config.add_static_view(name="lib", path="lib")

    # Register Chameleon rendederer also for .html-files
    config.add_renderer(".html", "pyramid.chameleon_zpt.renderer_factory")

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

    # Note: No ZODB for testing!

    # Configure traverse (for views that require access to the database)
    config.add_route("traversal", "/*traverse",
                     factory=lambda request: Application(request, {}))

    # Make WSGI app
    return config.make_wsgi_app()


class PyramidLayer(Layer):

    def setUp(self):
        self['config'] = testing.setUp(settings={})

        # Register Chameleon rendederer also for .html-files
        self['config'].add_renderer(".html",
                                    "pyramid.chameleon_zpt.renderer_factory")

        self['config'].scan("working_memory_games.app")
        self['config'].scan("working_memory_games.games")

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

    def stop(self):
        import sys
        for attr in ('stdin', 'stdout', 'stderr'):
            setattr(sys, attr, getattr(sys, '__%s__' % attr))
        import pdb
        pdb.set_trace()
