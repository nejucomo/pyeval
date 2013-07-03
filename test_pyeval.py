#! /usr/bin/env python

import sys
import unittest
from cStringIO import StringIO

import pyeval



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
