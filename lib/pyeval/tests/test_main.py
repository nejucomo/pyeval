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

    def test_helpAlias(self):
        fio = FakeIO()
        with fio:
            main(['help'])

        expected = fio.fakeout.getvalue()
        self.assertEqual('', fio.fakeerr.getvalue())

        for alias in ['-h', '--help']:
            fio = FakeIO()
            with fio:
                main([alias])

            self.assertEqual(expected, fio.fakeout.getvalue())
            self.assertEqual('', fio.fakeerr.getvalue())


