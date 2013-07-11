import unittest

from pyeval.main import main
from pyeval.tests.fakeio import FakeIO


class pyevalTests (unittest.TestCase):

    def test_fortytwo(self):
        fio = FakeIO()
        with fio:
            main(['42'])

        self.assertEqual('42\n', fio.fakeout.getvalue())
        self.assertEqual('', fio.fakeerr.getvalue())

