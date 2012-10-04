# -*- coding: utf-8 -*-
""" Tests for the main Application """

import unittest

from pyramid import testing

from working_memory_games import (
    app,
    datatypes
)

from working_memory_games.testing import INTEGRATION_TESTING


class AppIntegrationTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def test_app_no_player(self):
        request = testing.DummyRequest()
        context = app.Application(request, root={})
        result = app.select_player(context, request)

        self.assertEqual(result["players"], [])
        self.assertEqual(result["games"], [])

    def test_app_single_player(self):
        request = testing.DummyRequest()
        request.cookies["player_id"] = "foobar"

        root = {
            "players": {
                "foobar": datatypes.Player("John")
            }
        }

        context = app.Application(request, root=root)
        result = app.select_player(context, request)

        self.assertNotEqual(result["players"], [])
        self.assertNotEqual(result["games"], [])
