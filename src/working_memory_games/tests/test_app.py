# -*- coding: utf-8 -*-

import unittest
import json

from pyramid import testing

from persistent.mapping import PersistentMapping

from working_memory_games.app import Application
from working_memory_games.testing import INTEGRATION_TESTING
from working_memory_games.testing_utils import get_game_method


class AppIntegrationTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def test_guest_player_is_created(self):
        """Test that non-existing guest player can play game
        """

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

    def test_that_information_given_in_registration_form_is_stored(self):
        """Test all kind of data input in form of registration is actually
        stored to zodb.

        """

        request = testing.DummyRequest()
        app = Application(request, PersistentMapping())

        request.params.update({
            "name": "John",
            "age": "10",
            "gender": "m",  # f/m
            "adhd": True,
            "asperger": True,
            "narrow_wm": True,
            "concentration_difficulties": True,
            "email": "john.doe@example.com"
        })

        resp = app.create_new_player()

        self.assertEqual(type(resp), dict)
        self.assertIn("id", resp)

        player = app.data.players.get(resp.get("id"))
        self.assertEqual(player.name, request.params.get("name"))

        for detail in request.params.items():
            if detail[0] == "name":
                continue
            else:
                self.assertIn(detail, player.details.items())


class AppFunctionalTesting(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def play_one_session(self, app, player_id):
        app.request.cookies["active_player"] = player_id
        session = app.get_current_session(player_id)

        n = len(session.order)
        for i in range(n):
            next_game = app.get_next_game()
            self.assertEqual(session.order[0], next_game)

            game = app.games[next_game["game"]]
            method_name = get_game_method(game, "new", app.request)
            new_game = getattr(game, method_name)()

            items = new_game.get("items", new_game.get("sample", []))
            app.request.json_body = items
            game.save_fail()

        self.assertEqual(len(session.order), 0)

    def test_certain_method_gives_session_status_for_main_page(self):
        """ Main page indicates whether user has played the session
            for today. Should check status before, during and after session.
        """

        request = testing.DummyRequest()
        request.cookies["players"] = json.dumps([{'id':'123', 'name':'test'}])
        app = Application(request, PersistentMapping())

        result = app.get_session_statuses_for_today()
        self.assertEquals(result, [{'123': {'session_over': False}}])

        self.play_one_session(app, '123')

        result = app.get_session_statuses_for_today()
        self.assertEquals(result, [{'123': {'session_over': True}}])

    def test_after_session_game_redirects_to_main_page(self):
        """ Test for users that try to go to "pelaa" page after session.
            Should redirect to main page.
        """
        request = testing.DummyRequest()
        request.cookies["active_player"] = "123"
        app = Application(request, PersistentMapping())

        session = app.get_current_session()
        session.order = []
        try:
            app.get_next_game()
            assert False, u"No HTTPFound exception was raised."
        except Exception, e:
            redirect = 'http://example.com/#pelataan-taas-huomenna'
            self.assertIn(redirect, e.headers.values())

    def test_missing_active_player(self):
        """Test that missing cookie "active_player" will redirect to main page.
        """
        request = testing.DummyRequest()
        app = Application(request, PersistentMapping())

        try:
            app.get_current_session()
            assert False, u"No HTTPFound exception was raised."
        except Exception, e:
            redirect = 'http://example.com/'
            self.assertIn(redirect, e.headers.values())

    def get_game_stars_after_one_session(self, app, player_id):
        app.request.cookies["active_player"] = player_id

        name = next_game = app.get_next_game()
        while name == next_game:

            game = app.games[next_game["game"]]
            method_name = get_game_method(game, "new", app.request)
            new_game = getattr(game, method_name)()
            items = new_game.get("items", new_game.get("sample", []))
            app.request.json_body = items

            game.save_pass()

            next_game = app.get_next_game()

        return game.get_game_over().get("stars")

    def test_stars_two_at_start(self):
        """Test first game player has always two stars
        """
        player_id = '123'

        request = testing.DummyRequest()
        request.cookies["players"] = json.dumps([{
            'id': player_id, 'name': 'test'
        }])

        app = Application(request, PersistentMapping())
        stars = self.get_game_stars_after_one_session(app, player_id)

        self.assertEqual(stars, 2)

    def test_stars_three_when_better(self):
        """ Test second or later game with better result gives three stars
        """
        self.assertTrue(False)

    def test_stars_two_when_same(self):
        """Test second or later game with same result gives two stars
        """
        player_id = '123'

        request = testing.DummyRequest()
        request.cookies["players"] = json.dumps([{
            'id': player_id, 'name': 'test'
        }])

        app = Application(request, PersistentMapping())
        stars = self.get_game_stars_after_one_session(app, player_id)

        self.assertEqual(stars, 2)

    def test_stars_one_when_worse(self):
        """ Test second or later game with worse result gives one stars
        """
        self.assertTrue(False)

    def test_interrupted_game_wont_continue_day_later(self):
        """ If player quits the session before the session has ended
        the game shall not try to continue the same game on second day
        but have a new session. """
        self.assertTrue(False)

    def test_session_order(self):
        """Testaa, että pelikenttä vaihtuu pelin edetessä
        """
        request = testing.DummyRequest()
        request.cookies["active_player"] = "123"

        app = Application(request, PersistentMapping())

        session = app.get_current_session()

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

    def test_certain_percent_of_games_are_assisted(self):
        """ 30% of games should be assisted if assisted flag is set.
            Test that games are marked to be assisted.
        """
        request = testing.DummyRequest()
        app = Application(request, PersistentMapping())
        player_id = app.data.players.create_player("Guest", {
            "registered": False,
            "assisted": True
        })["id"]
        request.cookies["active_player"] = player_id

        session = app.get_current_session()
        n_assisted = len([game for game in session.order
                          if game.get("assisted") is True])
        portion_assisted = float(n_assisted) / len(session.order)
        self.assertGreater(portion_assisted, 0.3)
        self.assertLess(portion_assisted, 0.4)

    def test_at_least_95_of_200_of_new_players_are_assisted(self):
        """Test that almost half are assisted of new players.
        """
        request = testing.DummyRequest()
        app = Application(request, PersistentMapping())
        for i in range(200):
            app.create_new_guest()
        is_assisted = [player.details.get('assisted') for player
                       in app.data.players.values()]
        n_assisted = len(filter(bool, is_assisted))
        self.assertGreater(n_assisted, 95)
        self.assertLess(n_assisted, 105)

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
