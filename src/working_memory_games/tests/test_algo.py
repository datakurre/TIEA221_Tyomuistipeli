# -*- coding: utf-8 -*-

import unittest
import json

from pyramid import testing

from persistent.mapping import PersistentMapping

from working_memory_games.app import Application
from working_memory_games.testing import INTEGRATION_TESTING
from working_memory_games.testing_utils import (
    play_one_session,
    step_one_day,
    get_view_attr_name
)


class TestAlgorithm(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = testing.DummyRequest()
        self.app = Application(self.request, PersistentMapping())
        self.app.games = {u'numbers': self.app.games[u'numbers']}

    def test_passes_increase_level(self):
        """
        Pitäisi mennä näin:

        [True, True, True, True, True, True, True]
        Best n to present next: 3
        Best n to present next: 4
        Best n to present next: 6
        Best n to present next: 8
        Best n to present next: 10
        Best n to present next: 12
        Best n to present next: 14
        Best n to present next: 16

        Mutta meneekin näin:
        [päivä kello leveli oikein]
          2013-08-12
           rnumbers
             2013-08-12 08:12:40.245340 3 True
             2013-08-12 08:12:58.754654 4 True
             2013-08-12 08:13:15.736693 5 True
             2013-08-12 08:13:40.168772 5 True
          2013-08-13
           rnumbers
             2013-08-13 05:58:27.571994 5 True
             2013-08-13 05:58:50.802758 5 True
             2013-08-13 05:59:14.232525 5 True
             2013-08-13 05:59:33.848612 5 True
          2013-08-14
           rnumbers
             2013-08-14 12:09:42.463921 5 True
             2013-08-14 12:10:08.349395 5 True
             2013-08-14 12:10:28.589866 5 True
             2013-08-14 12:10:47.949320 5 True

        """

        expected_levels = [3,4,6,8,10,12,14,16]

        for level in expected_levels:
            player = play_one_try(self.app, '123', level)

def play_one_try(app, player_id, expected_level, save_pass=True):
    app.request.cookies["active_player"] = player_id
    session = app.get_current_session(player_id)
    session.order = [{'game': u'numbers', 'assisted': False} for i in range(2)]

    game = app.games.items()[0][1]
    method_name = get_view_attr_name(game, "new", app.request)
    new_game = getattr(game, method_name)()

    items = new_game.get("items", new_game.get("sample", []))
    assert new_game.get('level') == expected_level, \
        'expect '+str(expected_level)+', got '+str(new_game.get('level'))
    app.request.json_body = items

    if save_pass:
        game.save_pass()
    else:
        game.save_fail()

    return app.get_current_player(player_id)
