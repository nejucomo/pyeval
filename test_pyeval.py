#! /usr/bin/env python

import sys
import unittest
from cStringIO import StringIO

import pyeval



class AutoImporterTests (unittest.TestCase):
    def setUp(self):
        import logging
        self.logging = logging
        from logging import handlers
        self.handlers = handlers

        self.parent = pyeval.AutoImporter('logging')
        self.child = self.parent.handlers

    def test__ai_mod(self):
        self.assertIs(self.logging, self.parent._ai_mod)
        self.assertIs(self.handlers, self.child._ai_mod)

    def test__ai_parent(self):
        self.assertIs(None, self.parent._ai_parent)
        self.assertIs(self.logging, self.child._ai_parent)

    def test__ai_name(self):
        self.assertEqual('logging', self.parent._ai_name)
        self.assertEqual('handlers', self.child._ai_name)

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
        rawin = 'foo\n\n'
        stripin = rawin.strip()

        with FakeIO(rawin):
            self.assertEqual(rawin, self.scope['ri'])
            self.assertEqual(stripin, self.scope['i'])
            self.assertEqual(rawin, self.scope['ri'])
            self.assertEqual(stripin, self.scope['i'])

    def test_AutoImporterHook(self):
        # Pick a module that is not imported by default:
        self.assertIsInstance(self.scope['BaseHTTPServer'], pyeval.AutoImporter)



class FakeIO (object):
    def __init__(self, inbytes):
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
