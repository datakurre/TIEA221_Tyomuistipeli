# -*- coding: utf-8 -*-
"""Robot Framework test suite"""

import unittest

from plone.testing import layered
from robotsuite import RobotTestSuite

from working_memory_games.testing import ACCEPTANCE_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(RobotTestSuite('test_new_player.txt'),
                layer=ACCEPTANCE_TESTING),
        ])
    return suite
