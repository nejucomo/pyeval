import unittest
import pprint
from cStringIO import StringIO

import pyeval
from pyeval.tests.fakeio import FakeIO


class displayPrettyTests (unittest.TestCase):
    """displayPretty should behave like standard sys.displayhook, except pformat is used."""

    def test_displayNone(self):
        fio = FakeIO()

        with fio:
            pyeval.displayPretty(None)

        self.assertEqual('', fio.fakeout.getvalue())
        self.assertEqual('', fio.fakeerr.getvalue())

    def test_displayValues(self):
        for value in [42, "banana", range(1024), vars()]:
            f = StringIO()
            pprint.pprint(value, f)
            expected = f.getvalue()

            fio = FakeIO()

            with fio:
                pyeval.displayPretty(value)

            self.assertEqual(expected, fio.fakeout.getvalue())
            self.assertEqual('', fio.fakeerr.getvalue())
