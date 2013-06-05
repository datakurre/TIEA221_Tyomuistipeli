# -*- coding: utf-8 -*-
""" Tests for the main Application """

import unittest

from pyramid import testing

from persistent.mapping import PersistentMapping

from working_memory_games.app import Application

from working_memory_games.testing import INTEGRATION_TESTING


class AppIntegrationTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def test_guest_player_is_created(self):
        """Test that non-existing guest player can play game"""

        request = testing.DummyRequest()
        request.cookies["active_player"] = "123"
        app = Application(request, PersistentMapping())

        # Assertions
        # 0) Pelkkä etusivulla saapuminen ei luo pelaajaa
        self.assertNotIn("123", app.data.players)

        # 1) pitää olla olemassa ID:lle luotu pelaaja
        guest = app.get_current_player()
        self.assertIn("123", app.data.players)
        self.assertIsNotNone(guest)

        # 2) pitää olla anonyymi
        self.assertFalse(guest.details.get("registered"))
        self.assertIn(guest.details.get("assisted"), [True, False])

        # 3) pitää olla luotu pelit
        session = app.get_current_session()
        self.assertGreater(session.order, 0)


class AppFunctionalTesting(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def test_session_order(self):
        """ Testaa, että pelikenttä vaihtuu pelin edetessä
        """

        request = testing.DummyRequest()
        request.cookies["active_player"] = "123"

        # from webtest import TestApp
        # webapp = TestApp(self.layer["app"])
        # import pdb; pdb.set_trace()

        app = Application(request, PersistentMapping())

        session = app.get_current_session()

        def get_game_method(game, method_name, request):
            for adapter in request.registry.registeredAdapters():
                if len(adapter.required) > 2:
                    if adapter.required[2].providedBy(game):
                        if adapter.name == method_name:
                            return adapter.factory.__view_attr__

        n = len(session.order)
        for i in range(n):
            next_game = app.get_next_game()
            self.assertEqual(session.order[0], next_game)

            game = app.games[next_game["game"]]

            method_name = get_game_method(game, "new", request)
            new_game = getattr(game, method_name)()

            items = new_game.get("items", new_game.get("sample", []))
            request.json_body = items

            game.save_fail()

        self.assertEqual(len(session.order), 0)

    # def test_app_no_player(self):
    #     """Test empty application"""
    #     request = testing.DummyRequest()
    #     context = app.Application(request, PersistentMapping())
    #     result = app.select_player(context, request)
    #
    #     self.assertEqual(result["players"], [])
    #     self.assertEqual(result["games"], [])

    # def test_app_single_player(self):
    #     request = testing.DummyRequest()
    #     request.cookies["player_id"] = "foobar"
    #
    #     root = {
    #         "players": {
    #             "foobar": datatypes.Player("John")
    #         }
    #     }
    #
    #     context = app.Application(request, root=root)
    #     result = app.select_player(context, request)
    #
    #     self.assertNotEqual(result["players"], [])
    #     self.assertNotEqual(result["games"], [])
