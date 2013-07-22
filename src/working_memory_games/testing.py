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

        import select
        import waitress

        class WSGITestServer(waitress.server.WSGIServer):

            def run(self):
                try:
                    self.asyncore.loop(map=self._map)
                except (SystemExit, KeyboardInterrupt, select.error):
                    self.task_dispatcher.shutdown()

            def stop(self):
                for socket in self._map.values():
                    socket.close()

        self['server'] = WSGITestServer(
            self['app'], port=int(os.environ.get("HTTP_PORT", 55002)))

        from threading import Thread
        self['thread'] = Thread(target=self['server'].run)
        self['thread'].start()

    def testTearDown(self):
        self['server'].stop()

        del self['app']

ACCEPTANCE_TESTING = PyramidServerLayer()
