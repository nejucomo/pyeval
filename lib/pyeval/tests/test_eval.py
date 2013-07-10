import unittest
from types import ModuleType
import math

from pyeval.eval import pyeval



class pyevalTests (unittest.TestCase):
    """High-level tests of pyeval.eval.pyeval."""

    def test_autoimportTopLevel(self):
        self.assertIs(math, pyeval('math')._ai_mod)

    def test_autoimportSubmodule(self):
        ai = pyeval('faketestpackage.faketestmodule')
        self.assertIs(ModuleType, type(ai._ai_mod))

    def test_unboundRaisesNameError(self):
        self.assertRaises(NameError, pyeval, 'BLORK_IS_NOT_BOUND')
