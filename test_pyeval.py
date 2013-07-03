#! /usr/bin/env python

import sys
import unittest
from types import ModuleType
from pprint import pprint
from cStringIO import StringIO

import pyeval



class pyevalTests (unittest.TestCase):
    """High-level tests of pyeval.pyeval."""

    def test_autoimportTopLevel(self):
        import math
        self.assertIs(math, pyeval.pyeval('math')._ai_mod)

    def test_autoimportSubmodule(self):
        ai = pyeval.pyeval('faketestpackage.faketestmodule')
        self.assertIs(ModuleType, type(ai._ai_mod))



class displayTests (unittest.TestCase):
    """display should behave like standard sys.displayhook, except pformat is used."""

    def test_displayNone(self):
        fio = FakeIO()

        with fio:
            pyeval.display(None)

        self.assertEqual('', fio.fakeout.getvalue())
        self.assertEqual('', fio.fakeerr.getvalue())

    def test_displayValues(self):
        for value in [42, "banana", range(1024), vars()]:
            f = StringIO()
            pprint(value, f)
            expected = f.getvalue()

            fio = FakeIO()

            with fio:
                pyeval.display(value)

            self.assertEqual(expected, fio.fakeout.getvalue())
            self.assertEqual('', fio.fakeerr.getvalue())



class AutoImporterTests (unittest.TestCase):
    def setUp(self):
        import logging
        self.logging = logging
        from logging import handlers
        self.handlers = handlers

        self.parent = pyeval.AutoImporter(pyeval.import_last('logging'))
        self.child = self.parent.handlers

    def test___repr__(self):
        r = repr(self.child)
        self.assertNotEqual(-1, r.find('AutoImporter'))
        self.assertNotEqual(-1, r.find('logging.handlers'))

    def test__ai_mod(self):
        self.assertIs(self.logging, self.parent._ai_mod)
        self.assertIs(self.handlers, self.child._ai_mod)

    def test__ai_parent(self):
        self.assertIs(None, self.parent._ai_parent)
        self.assertIs(self.parent, self.child._ai_parent)

    def test__ai_fullname(self):
        self.assertEqual('logging', self.parent._ai_fullname)
        self.assertEqual('logging.handlers', self.child._ai_fullname)

    def test_attr(self):
        self.assertIs(self.logging.basicConfig, self.parent.basicConfig)
        self.assertIs(self.handlers.MemoryHandler, self.child.MemoryHandler)



class MagicScopeTests (unittest.TestCase):
    def setUp(self):
        self.scope = pyeval.MagicScope()

    def test_inputCaching(self):
        rawin = 'foo\nbar\n\n'
        stripin = rawin.strip()
        rlines = rawin.split('\n')
        lines = [ l.strip() for l in rlines ]

        with FakeIO(rawin):
            for i in range(2):
                self.assertEqual(rawin, self.scope['ri'])
                self.assertEqual(stripin, self.scope['i'])
                self.assertEqual(rlines, self.scope['rlines'])
                self.assertEqual(lines, self.scope['lines'])

    def test_AutoImporterHook(self):
        # Pick a module that is not imported by default:
        self.assertIsInstance(self.scope['BaseHTTPServer'], pyeval.AutoImporter)



class FakeIO (object):
    def __init__(self, inbytes=''):
        self.inbytes = inbytes

    def __enter__(self):
        self.realout = sys.stdout
        self.realerr = sys.stderr
        self.realin = sys.stdin

        self.fakeout = sys.stdout = StringIO()
        self.fakeerr = sys.stderr = StringIO()
        self.fakein = sys.stdin = StringIO(self.inbytes)

        return self

    def __exit__(self, *a):
        sys.stdout = self.realout
        sys.stderr = self.realerr
        sys.stdin = self.realin



if __name__ == '__main__':
    unittest.main()
