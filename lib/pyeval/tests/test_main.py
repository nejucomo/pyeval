import unittest
import math

from pyeval.main import main



class mainTests (unittest.TestCase):

    def _test_main(self, expected, args):
        displays = []
        main(args, displays.append)
        self.assertEqual([expected], displays)

    def test_a1(self):
        self._test_main('B', ['a1', 'A', 'B', 'C'])

    def test_42(self):
        self._test_main(42, ['42', 'A', 'B', 'C'])

    def test_math_pi(self):
        self._test_main(math.pi, ['math.pi', 'A', 'B', 'C'])
