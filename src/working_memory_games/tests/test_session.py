# -*- coding: utf-8 -*-

import unittest
import json

from pyramid import testing

from persistent.mapping import PersistentMapping
from pyramid.httpexceptions import HTTPFound

from working_memory_games.app import Application
from working_memory_games.testing import INTEGRATION_TESTING
from working_memory_games.testing_utils import (
    get_view_method,
    play_one_session,
    step_one_day
)


class TestSession(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = testing.DummyRequest()
        self.app = Application(self.request, PersistentMapping())

    def test_certain_method_gives_session_status_for_main_page(self):
        """Main page indicates whether user has played the session for today.
        Should check status before, during and after session.

        """
        self.request.cookies["players"] = json.dumps([{
            'id': '123',
            'name': 'test'
        }])

        result = self.app.get_session_statuses_for_today()
        self.assertEquals(result, [{'123': {'session_over': False}}])

        play_one_session(self.app, '123')

        result = self.app.get_session_statuses_for_today()
        self.assertEquals(result, [{'123': {'session_over': True}}])

    def test_after_session_game_redirects_to_main_page(self):
        """Test for users that try to go to "pelaa" page after session. Should
        redirect to main page.

        """
        self.request.cookies["active_player"] = "123"

        session = self.app.get_current_session()
        session.order = []
        try:
            self.app.get_next_game()
            assert False, u"No HTTPFound exception was raised."
        except HTTPFound, e:
            redirect = 'http://example.com/#pelataan-taas-huomenna'
            self.assertIn(redirect, e.headers.values())

    def test_interrupted_game_wont_continue_day_later(self):
        """If player quits the session before the session has ended the game
        shall not try to continue the same game on second day but have a new
        session

        """
        self.request.cookies["players"] = json.dumps([{
            'id': '123',
            'name': 'test'
        }])

        player = play_one_session(self.app, '123', percentage=80)
        self.assertGreater(
            len(self.app.get_current_session('123').order), 0,
            u"Session was completed when it shouldn't.")
        self.assertLess(
            len(player), 2, u"More than one session was played.")

        step_one_day(self.app, '123')
        player = play_one_session(self.app, '123')

        self.assertGreater(
            len(player), 1, u"New session was not started.")
        self.assertLess(
            len(player), 3, u"More than two sessions were played.")

    def test_session_order(self):
        """Testaa, että pelikenttä vaihtuu pelin edetessä
        """

        self.request.cookies["active_player"] = "123"

        session = self.app.get_current_session()

        n = len(session.order)
        for i in range(n):
            next_game = self.app.get_next_game()
            self.assertEqual(session.order[0], next_game)

            game = self.app.games[next_game["game"]]

            method_name = get_view_method(game, "new", self.request)
            new_game = getattr(game, method_name)()

            items = new_game.get("items", new_game.get("sample", []))
            self.request.json_body = items

            game.save_fail()

        self.assertEqual(len(session.order), 0)

    def test_certain_percent_of_games_are_assisted(self):
        """Test that 30% of games should be assisted if assisted flag is set.
        Test that games are marked to be assisted.

        """
        player_id = self.app.data.players.create_player("Guest", {
            "registered": False,
            "assisted": True
        })["id"]
        self.request.cookies["active_player"] = player_id

        session = self.app.get_current_session()
        n_assisted = len([game for game in session.order
                          if game.get("assisted") is True])
        portion_assisted = float(n_assisted) / len(session.order)
        self.assertGreaterEqual(portion_assisted, 0.3)
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
