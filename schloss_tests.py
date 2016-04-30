# -*- coding: utf-8 -*-

import unittest

from schloss import *


class SchlossTest(unittest.TestCase):
    def test_decode_keypad(self):
        key_1 = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]]
        self.assertEquals(decode_keypad(key_1), '1')

    def test_decrease_timeouts(self):
        timeouts_expected = {'1': 0}
        timeouts_input = {'1': 1}
        result = decrease_timeouts(timeouts_input)
        self.assertEquals(timeout_expected, result)
        result = decrease_timeouts(result)
        self.assertEquals(timeout_expected, result)

