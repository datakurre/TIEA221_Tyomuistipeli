# -*- coding: utf-8 -*-

import os
from pyramid.renderers import JSON
from pyramid import testing

from plone.testing import Layer
from working_memory_games.app import Application
from working_memory_games import main


json_renderer = JSON()


class PyramidLayer(Layer):

    def setUp(self):
        self['config'] = testing.setUp(settings={})

        self['config'].add_renderer(
            ".html", "pyramid.chameleon_zpt.renderer_factory")
        self['config'].add_renderer(
            "json", json_renderer)

        self['config'].add_route(
            "root", "/")
        self['config'].add_route(
            "register", "/liity", request_method="GET")
        self['config'].add_route(
            "traversal", "/*traverse", factory=Application)

        self['config'].scan("working_memory_games.app")
        self['config'].scan("working_memory_games.games")

    def tearDown(self):
        testing.tearDown()
        del self['config']

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass

INTEGRATION_TESTING = PyramidLayer()


class PyramidAppLayer(Layer):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSetUp(self):
        self['app'] = main({}, **{"zodbconn.uri": "memory://"})

    def testTearDown(self):
        del self['app']


FUNCTIONAL_TESTING = PyramidAppLayer()


class PyramidServerLayer(Layer):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSetUp(self):
        self['app'] = main({}, **{"zodbconn.uri": "memory://"})

        from wsgiref.simple_server import make_server
        self['server'] = make_server(
            '', int(os.environ.get("HTTP_PORT", 55002)), self['app'])
        self['server'].RequestHandlerClass.log_request =\
            lambda self, code, size: None  # mute http server
        self['server'].timeout = 0.5  # set handle request timeout

        from threading import Thread
        self['thread'] = Thread(target=self['server'].serve_forever)
        self['thread'].start()

    def testTearDown(self):
        self['server'].shutdown()
        self['server'].server_close()

        del self['app']

ACCEPTANCE_TESTING = PyramidServerLayer()
