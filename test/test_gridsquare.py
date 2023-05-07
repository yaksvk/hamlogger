#!/usr/bin/env python3

import unittest
from collections import namedtuple
C = namedtuple('Case', 'input output')

from lib.gridsquare import is_gridsquare
from lib.gridsquare import extract_gridsquare
from lib.gridsquare import small_square_distance
from lib.gridsquare import gridsquare2latlng
from lib.gridsquare import gridsquare2latlngedges
from lib.gridsquare import dist_haversine
from lib.gridsquare import dist_ham



class TestGridsquare(unittest.TestCase):

    def test_is_gridsquare(self):
        cases = (
            C(None, False),
            C('', False),
            C('jn88nc', True),
        )
        for c in cases:
            self.assertEqual(is_gridsquare(c.input), c.output)
