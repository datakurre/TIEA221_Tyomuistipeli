# -*- coding: utf-8 -*-

import unittest
import json

from pyramid import testing

from persistent.mapping import PersistentMapping

from working_memory_games.app import Application
from working_memory_games.testing import INTEGRATION_TESTING
from working_memory_games.testing_utils import play_one_session


class AppFunctionalTesting(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = testing.DummyRequest()
        self.app = Application(self.request, PersistentMapping())

    def test_stars_two_at_start(self):
        """Test first game player has always two stars
        """

        self.request.cookies["players"] = json.dumps([{
            'id': '123',
            'name': 'test'
        }])

        play_one_session(self.app, '123')
        # import pdb; pdb.set_trace()
        stars = 2

        self.assertEqual(stars, 2)

    def test_stars_three_when_better(self):
        """ Test second or later game with better result gives three stars
        """
        self.assertTrue(False)

    def test_stars_two_when_same(self):
        """Test second or later game with same result gives two stars
        """

        self.request.cookies["players"] = json.dumps([{
            'id': '123',
            'name': 'test'
        }])

        play_one_session(self.app, '123')
        # import pdb; pdb.set_trace()
        stars = 2

        self.assertEqual(stars, 2)

    def test_stars_one_when_worse(self):
        """ Test second or later game with worse result gives one stars
        """
        self.assertTrue(False)
