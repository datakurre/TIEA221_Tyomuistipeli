# -*- coding: utf-8 -*-

import unittest

from pyramid import testing

from persistent.mapping import PersistentMapping

from working_memory_games.app import Application
from working_memory_games.testing import INTEGRATION_TESTING


class PlayerTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = testing.DummyRequest()
        self.app = Application(self.request, PersistentMapping())

    def test_guest_player_is_created(self):
        """Test that non-existing guest player can play game
        """

        self.request.cookies["active_player"] = "123"

        # Assertions
        # 0) Pelkkä etusivulla saapuminen ei luo pelaajaa
        self.assertNotIn("123", self.app.data.players)

        # 1) pitää olla olemassa ID:lle luotu pelaaja
        guest = self.app.get_current_player()
        self.assertIn("123", self.app.data.players)
        self.assertIsNotNone(guest)

        # 2) pitää olla anonyymi
        self.assertFalse(guest.details.get("registered"))
        self.assertIn(guest.details.get("assisted"), [True, False])

        # 3) pitää olla luotu pelit
        session = self.app.get_current_session()
        self.assertGreater(session.order, 0)

    def test_missing_active_player(self):
        """Test that missing cookie "active_player" will redirect to main page.
        """
        try:
            self.app.get_current_session()
            assert False, u"No HTTPFound exception was raised."
        except Exception, e:
            redirect = 'http://example.com/'
            self.assertIn(redirect, e.headers.values())

    def test_that_information_given_in_registration_form_is_stored(self):
        """Test all kind of data input in form of registration is actually
        stored to zodb.

        """
        self.request.params.update({
            "name": "John",
            "age": "10",
            "gender": "m",  # f/m
            "adhd": True,
            "asperger": True,
            "narrow_wm": True,
            "concentration_difficulties": True,
            "email": "john.doe@example.com"
        })

        resp = self.app.create_new_player()

        self.assertEqual(type(resp), dict)
        self.assertIn("id", resp)

        player = self.app.data.players.get(resp.get("id"))
        self.assertEqual(player.name, self.request.params.get("name"))

        for detail in self.request.params.items():
            if detail[0] == "name":
                continue
            else:
                self.assertIn(detail, player.details.items())
