#!/usr/bin/env python3

import unittest
from collections import namedtuple
C = namedtuple('Case', 'input output')

from lib.models import CallsignEntity


class TestCallsignEntity(unittest.TestCase):

    def test_callsign_conversion(self):
        cases = (
            C('OE/OM1WS/P', 'OM1WS'),
            C('S5/OM1WS', 'OM1WS'),
            C('OM1WS/MM', 'OM1WS'),
            C('OE1WED/3', 'OE1WED'),
        )
        for c in cases:
            self.assertEqual(CallsignEntity.get_base_callsign(c.input), c.output)
