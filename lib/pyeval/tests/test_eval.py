import unittest
import math
from types import FunctionType

from pyeval.help import HelpBrowser
from pyeval.autoimporter import AutoImporter
from pyeval.eval import pyeval, buildStandardMagicScope
from pyeval.tests.fakeio import FakeIO



class pyevalTests (unittest.TestCase):
    """High-level tests of pyeval.eval.pyeval."""

    def test_autoimportTopLevel(self):
        self.assertIs(math, pyeval('ai.mod(math)'))

    def test_args(self):
        self.assertEqual(('x', 'y'), pyeval('args', 'x', 'y'))
        self.assertEqual('x', pyeval('a0', 'x', 'y'))
        self.assertEqual('y', pyeval('a1', 'x', 'y'))
        self.assertRaises(NameError, pyeval, 'a2', 'x', 'y')

    def test_autoimportSubmodule(self):
        proxy = pyeval('faketestpackage.faketestmodule')
        self.assertIsInstance(proxy, AutoImporter.Proxy)

    def test_unboundRaisesNameError(self):
        self.assertRaises(NameError, pyeval, 'BLORK_IS_NOT_BOUND')


class StandardMagicScopeTests (unittest.TestCase):
    def setUp(self):
        self.imports = []

        class FakeAutoImporter (object):
            def proxyImport(_, name):
                self.imports.append(name)

        self.fakeai = FakeAutoImporter()

        self.args = ['foo', 'bar']
        self.scope = buildStandardMagicScope(self.args, self.fakeai)

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
                self.assertIsInstance(self.scope['help'], HelpBrowser)

    def test_fallthrough(self):
        key = '6ff25ffc'
        x = self.scope[key]
        self.assertIsNone(x)
        self.assertEqual([key], self.imports)

    def test_registerMagic(self):

        callCount = [0]

        @self.scope.registerMagic
        def x():
            callCount[0] += 1
            return callCount[0]

        self.assertEqual(1, self.scope['x'])
        self.assertEqual(1, self.scope['x'])
        self.assertEqual(1, self.scope['x'])

    def test_getMagicDocs(self):
        for (k, v) in self.scope.getMagicDocs():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, str)

    def test_magic_sh(self):

        def test_output(arg, expected):
            sh = self.scope['sh']

            fio = FakeIO()
            with fio:
                result = sh(arg)

            self.assertIsNone(result, 'sh() returned non-None: %r' % (result,))
            self.assertEqual(expected, fio.fakeout.getvalue())
            self.assertEqual('', fio.fakeerr.getvalue())

        test_output(None, '')
        test_output('foo', 'foo\n')
        test_output(42, '42\n')
        test_output(['foo', 42], 'foo\n42\n')
        test_output( ( x for x in ['foo', 42] ), 'foo\n42\n')
        test_output( {'x': 'xylophone', 'y': 'yam'}, 'y\nx\n')

    def test_magicFunctionNamesMatchBinding(self):
        for (name, _) in self.scope.getMagicDocs():
            with FakeIO():
                value = self.scope[name]

            if isinstance(value, FunctionType):
                self.assertEqual(name, value.__name__)
