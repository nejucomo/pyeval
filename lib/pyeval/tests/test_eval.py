import unittest
import math

from pyeval.autoimporter import AutoImporter
from pyeval.eval import pyeval



class pyevalTests (unittest.TestCase):
    """High-level tests of pyeval.eval.pyeval."""

    def test_autoimportTopLevel(self):
        self.assertIs(math, pyeval('ai.mod(math)'))

    def test_autoimportSubmodule(self):
        proxy = pyeval('faketestpackage.faketestmodule')
        self.assertIsInstance(proxy, AutoImporter.Proxy)

    def test_unboundRaisesNameError(self):
        self.assertRaises(NameError, pyeval, 'BLORK_IS_NOT_BOUND')
