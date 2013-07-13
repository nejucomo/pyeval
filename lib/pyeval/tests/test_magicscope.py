import unittest

from pyeval.magic.scope import MagicScope



class MagicScopeTests (unittest.TestCase):
    def setUp(self):
        self.caught = []
        self.scope = MagicScope(self.caught.append)

    def test_registerMagic(self):

        @self.scope.registerMagic
        def scope(scope):
            """the scope"""
            return scope

        self.assertIs(self.scope, self.scope['scope'])

    def test_registerMagicFunction(self):

        @self.scope.registerMagicFunction
        def f(scope, x):
            """the scope and x"""
            return (scope, x)

        (scope, v) = self.scope['f'](42)
        self.assertIs(self.scope, scope)
        self.assertEqual(42, v)

    def test_fallthrough(self):
        key = '6ff25ffc'
        x = self.scope[key]
        self.assertIsNone(x)
        self.assertEqual([key], self.caught)

    def test_inputCaching(self):

        callCount = [0]

        @self.scope.registerMagic
        def x(scope):
            callCount[0] += 1
            return callCount[0]

        self.assertEqual(1, self.scope['x'])
        self.assertEqual(1, self.scope['x'])
        self.assertEqual(1, self.scope['x'])

    def test_getMagicDocs(self):
        @self.scope.registerMagic
        def x(scope):
            """docs for x"""

        @self.scope.registerMagic
        def y(scope):
            """docs for x"""

        for (k, v) in self.scope.getMagicDocs():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, str)


class MagicScopeDictInterfaceTests (unittest.TestCase):
    def setUp(self):

        def failIfCalled(key):
            self.fail('A magic scope operation fell through unexpectedly.')

        self.scope = MagicScope(failIfCalled)

        self.scope['x'] = 0

        @self.scope.registerMagic
        def y(scope):
            """y docs"""
            return 1

    def test___repr__(self):
        # The repr should *not* delegate to dict, because some magic
        # values trigger IO:
        self.assertRegexpMatches(repr(self.scope), r'<MagicScope \[.*\]>$')

    def _testInvariantEquality(self, expected, f, *args):
        self.assertEqual(expected, f(*args))

        self.scope['y'] # Resolve the magic variable.

        # Repeat the invariant:
        self.assertEqual(expected, f(*args))

    def test___len__(self):
        self._testInvariantEquality(2, len, self.scope)

    def test_keys(self):
        self._testInvariantEquality(['x', 'y'], lambda : sorted(self.scope.keys()))

    def test_values(self):
        self._testInvariantEquality([0, 1], lambda : sorted(self.scope.values()))

    def test_items(self):
        self._testInvariantEquality([('x', 0), ('y', 1)], lambda : sorted(self.scope.items()))

    def test_iterkeys(self):
        self._testInvariantEquality(['x', 'y'], lambda : sorted(self.scope.iterkeys()))

    def test_itervalues(self):
        self._testInvariantEquality([0, 1], lambda : sorted(self.scope.itervalues()))

    def test_iteritems(self):
        self._testInvariantEquality([('x', 0), ('y', 1)], lambda : sorted(self.scope.iteritems()))

