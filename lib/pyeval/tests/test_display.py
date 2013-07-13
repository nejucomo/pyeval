import unittest
import pprint
from cStringIO import StringIO

from pyeval.display import displayPretty
from pyeval.tests.fakeio import FakeIO


class displayPrettyTests (unittest.TestCase):
    """displayPretty should behave like standard sys.displayhook, except pformat is used."""

    def test_displayNone(self):
        fio = FakeIO()

        with fio:
            displayPretty(None)

        fio.checkLiteral(self, '', '')

    def test_displayValues(self):
        for value in [42, "banana", range(1024), vars()]:
            f = StringIO()
            pprint.pprint(value, f)
            expected = f.getvalue()

            fio = FakeIO()

            with fio:
                displayPretty(value)

            fio.checkLiteral(self, expected, '')
