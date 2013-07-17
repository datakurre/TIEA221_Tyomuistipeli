# -*- coding: utf-8 -*-

import unittest

from plone.testing import layered
from robotsuite import RobotTestSuite

from working_memory_games.testing import ACCEPTANCE_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(RobotTestSuite('test_main_menu.robot'),
               layer=ACCEPTANCE_TESTING),
    ])
    return suite
