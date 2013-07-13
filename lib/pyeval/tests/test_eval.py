import unittest
import sys
import math
from types import FunctionType

from pyeval.help import HelpBrowser
from pyeval.autoimporter import AutoImporter
from pyeval.eval import pyeval, pyevalAndDisplay, buildStandardMagicScope
from pyeval.tests.fakeio import FakeIO



class pyevalTests (unittest.TestCase):
    def test_autoimportTopLevel(self):
        self.assertIs(math, pyeval('ai.mod(math)'))

    def test_args(self):
        self.assertEqual(('x', 'y'), pyeval('args', 'x', 'y'))
        self.assertEqual('x', pyeval('a0', 'x', 'y'))
        self.assertEqual('y', pyeval('a1', 'x', 'y'))
        self.assertRaises(NameError, pyeval, 'a2', 'x', 'y')

    def test_autoimportSubmodule(self):
        proxy = pyeval('cStringIO')
        self.assertIsInstance(proxy, AutoImporter.Proxy)

    def test_unboundRaisesNameError(self):
        self.assertRaises(NameError, pyeval, 'BLORK_IS_NOT_BOUND')


class pyevalAndDisplayTests (unittest.TestCase):

    def _test_pead(self, expected, args):
        displays = []
        pyevalAndDisplay(displayhook=displays.append, *args)
        self.assertEqual([expected], displays)

    def test_a1(self):
        self._test_pead('B', ['a1', 'A', 'B', 'C'])

    def test_42(self):
        self._test_pead(42, ['42', 'A', 'B', 'C'])

    def test_math_pi(self):
        self._test_pead(math.pi, ['math.pi', 'A', 'B', 'C'])

    def test_displayhookReset(self):
        hook = lambda _: None
        pyevalAndDisplay('42', displayhook=hook)
        self.assertIsNot(hook, sys.displayhook)

    def test_displayhookNoTouch(self):
        hook = lambda _: None
        sys.displayhook = hook
        pyevalAndDisplay('42', displayhook=None)
        self.assertIs(hook, sys.displayhook)

    def test_unexpectedKeyword(self):
        self.assertRaises(TypeError, pyevalAndDisplay, '42', wombat='monkey')


class StandardMagicScopeTests (unittest.TestCase):
    def setUp(self):
        self.imports = []

        class FakeAutoImporter (object):
            def proxyImport(_, name):
                self.imports.append(name)

        self.fakeai = FakeAutoImporter()

        self.args = ['foo', 'bar']
        self.scope = buildStandardMagicScope(self.args, self.fakeai)

    def test_conciseBindings(self):
        # The standard MagicScope delegates to __builtin__ in its
        # fallthrough, rather than dumping all builtins into the dict.
        # This keeps the output short and relevant of:
        # $ pyeval 'dir()'

        self.assertEqual(len(self.scope), len(self.scope.getMagicDocs()))

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
        def x(scope):
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
            fio.checkLiteral(self, expected, '')

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
