import unittest

from pyeval.main import main
from pyeval.tests.fakeio import FakeIO


class pyevalTests (unittest.TestCase):

    def test_fortytwo(self):
        fio = FakeIO()
        with fio:
            main(['42'])

        fio.checkLiteral(self, '42\n', '')

    def test_helpAlias(self):
        fio = FakeIO()
        with fio:
            main(['help'])

        (expected, error) = fio.getOutputs()
        self.assertEqual('', error)

        for args in [[], ['-h'], ['--help']]:
            fio = FakeIO()
            with fio:
                main(args)

            fio.checkLiteral(self, expected, '')

    def test_scopeRepr(self):
        fio = FakeIO()
        with fio:
            main(['scope'])

        fio.checkRegexp(self, '^<MagicScope \[.*\]>$', '^$')

