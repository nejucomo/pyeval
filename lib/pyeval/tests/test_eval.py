import unittest
import math

from pyeval.autoimporter import AutoImporter
from pyeval.eval import pyeval



class pyevalTests (unittest.TestCase):
    """High-level tests of pyeval.eval.pyeval."""

    def test_autoimportTopLevel(self):
        self.assertIs(math, pyeval('ai.mod(math)'))

    def test_args(self):
        self.assertEqual(('x', 'y'), pyeval('args', 'x', 'y'))
        self.assertEqual('x', pyeval('a0', 'x', 'y'))
        self.assertEqual('y', pyeval('a1', 'x', 'y'))
        self.assertRaises(NameError, pyeval, 'a2', 'x', 'y')

    def test_autoimportSubmodule(self):
        proxy = pyeval('faketestpackage.faketestmodule')
        self.assertIsInstance(proxy, AutoImporter.Proxy)

    def test_unboundRaisesNameError(self):
        self.assertRaises(NameError, pyeval, 'BLORK_IS_NOT_BOUND')
