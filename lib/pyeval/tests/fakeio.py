__all__ = ['FakeIO']


import sys
from cStringIO import StringIO



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



