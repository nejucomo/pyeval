__all__ = ['FakeIO']


import re
import sys
from cStringIO import StringIO



class FakeIO (object):
    def __init__(self, inbytes=''):
        self._inbytes = inbytes

    def __enter__(self):
        self._realout = sys.stdout
        self._realerr = sys.stderr
        self._realin = sys.stdin

        self._fakeout = sys.stdout = StringIO()
        self._fakeerr = sys.stderr = StringIO()
        self._fakein = sys.stdin = StringIO(self._inbytes)

        return self

    def __exit__(self, *a):
        sys.stdout = self._realout
        sys.stderr = self._realerr
        sys.stdin = self._realin

    # Unittest verification API:
    def getOutputs(self):
        return (self._fakeout.getvalue(), self._fakeerr.getvalue())

    def checkLiteral(self, testcase, expectedOut, expectedError):
        self.checkRegexp(testcase, re.escape(expectedOut), re.escape(expectedError))

    def checkRegexp(self, testcase, expectedOut, expectedError):
        (output, error) = self.getOutputs()
        testcase.assertRegexpMatches(output, expectedOut)
        testcase.assertRegexpMatches(error, expectedError)


