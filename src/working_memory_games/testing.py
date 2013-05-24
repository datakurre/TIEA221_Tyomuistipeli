# -*- coding: utf-8 -*-
""" Test layers for zope.testrunner """

import os

from pyramid.renderers import JSON

json_renderer = JSON()

from plone.testing import Layer

from pyramid import testing

from pyramid.config import Configurator

from working_memory_games import static_file
from working_memory_games.app import Application

from working_memory_games import main


class PyramidLayer(Layer):

    def setUp(self):
        self['config'] = testing.setUp(settings={})

        self['config'].add_renderer(
                ".html", "pyramid.chameleon_zpt.renderer_factory")
        self['config'].add_renderer(
                "json", json_renderer)

        self['config'].add_route("root", "/")
        self['config'].add_route("register", "/liity", request_method="GET")

        self['config'].add_route("traversal", "/*traverse", factory=Application)

        self['config'].scan("working_memory_games.app")
        self['config'].scan("working_memory_games.games")


    def tearDown(self):
        testing.tearDown()

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass

INTEGRATION_TESTING = PyramidLayer()


class PyramidAppLayer(Layer):

    def setUp(self):
        self['app'] = main({}, testing=True)

    def tearDown(self):
        testing.tearDown()

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass

FUNCTIONAL_TESTING = PyramidAppLayer()


class PyramidServerLayer(Layer):

    def setUp(self):
        self['app'] = main({}, testing=True)

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
