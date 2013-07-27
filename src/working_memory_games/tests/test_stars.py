# -*- coding: utf-8 -*-

import unittest
import json

from pyramid import testing

from persistent.mapping import PersistentMapping

from working_memory_games.app import Application
from working_memory_games.testing import INTEGRATION_TESTING
from working_memory_games.testing_utils import (
    play_one_session,
    step_one_day
)


class TestStars(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = testing.DummyRequest()
        self.app = Application(self.request, PersistentMapping())
        self.app.games = dict((self.app.games.items()[0],))

    def test_stars_two_at_start(self):
        """Test first game player has always two stars
        """
        self.request.cookies["players"] = json.dumps([{
            'id': '123',
            'name': 'test'
        }])

        player = play_one_session(self.app, '123')

        self.assertGreater(
            len(player), 0, u"No sessions was played.")
        self.assertEqual(
            len(player), 1, u"More than one session was played.")
        self.assertGreater(
            len(player.values()[0]), 0, u"No games were played.")

        some_game = tuple(player.values()[0].keys())[0]

        self.assertIn(
            some_game, self.app.games, u"Game not found.")

        game = self.app.games[some_game]

        self.assertEqual(game.get_game_over()["stars"], 2)

    def test_stars_three_when_better(self):
        """ Test second or later game with better result gives three stars
        """
        self.request.cookies["players"] = json.dumps([{
            'id': '123',
            'name': 'test'
        }])

        play_one_session(self.app, '123', save_pass=[True, False] * 100)
        step_one_day(self.app, '123')
        player = play_one_session(self.app, '123', save_pass=[True] * 100)

        self.assertGreater(
            len(player), 1, u"Only one session was played.")
        self.assertLess(
            len(player), 3, u"More than two sessions were played.")

        some_game = tuple(player.values()[0].keys())[0]

        self.assertIn(
            some_game, self.app.games, u"Game not found.")

        game = self.app.games[some_game]

        self.assertEqual(game.get_game_over()["stars"], 3)

    def test_stars_two_when_same(self):
        """Test second or later game with same result gives two stars
        """
        self.request.cookies["players"] = json.dumps([{
            'id': '123',
            'name': 'test'
        }])

        play_one_session(self.app, '123', save_pass=[False] * 100)
        step_one_day(self.app, '123')
        player = play_one_session(self.app, '123', save_pass=[False] * 100)

        self.assertGreater(
            len(player), 1, u"Only one session was played.")
        self.assertLess(
            len(player), 3, u"More than two sessions were played.")

        some_game = tuple(player.values()[0].keys())[0]

        self.assertIn(
            some_game, self.app.games, u"Game not found.")

        game = self.app.games[some_game]

        self.assertEqual(game.get_game_over()["stars"], 2)

    def test_stars_one_when_worse(self):
        """ Test second or later game with worse result gives one stars
        """
        self.request.cookies["players"] = json.dumps([{
            'id': '123',
            'name': 'test'
        }])

        play_one_session(self.app, '123', save_pass=[True] * 100)
        step_one_day(self.app, '123')
        player = play_one_session(self.app, '123', save_pass=[False] * 100)

        self.assertGreater(
            len(player), 1, u"Only one session was played.")
        self.assertLess(
            len(player), 3, u"More than two sessions were played.")

        some_game = tuple(player.values()[0].keys())[0]

        self.assertIn(
            some_game, self.app.games, u"Game not found.")

        game = self.app.games[some_game]

        self.assertEqual(game.get_game_over()["stars"], 1)
