import unittest

from pyeval.magic.scope import MagicScope



class MagicScopeTests (unittest.TestCase):
    def setUp(self):
        self.caught = []
        self.scope = MagicScope(self.caught.append)

    def test_fallthrough(self):
        key = '6ff25ffc'
        x = self.scope[key]
        self.assertIsNone(x)
        self.assertEqual([key], self.caught)

    def test_inputCaching(self):

        callCount = [0]

        @self.scope.registerMagic
        def x():
            callCount[0] += 1
            return callCount[0]

        self.assertEqual(1, self.scope['x'])
        self.assertEqual(1, self.scope['x'])
        self.assertEqual(1, self.scope['x'])

    def test_getMagicDocs(self):
        @self.scope.registerMagic
        def x(self):
            """docs for x"""

        @self.scope.registerMagic
        def y(self):
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
        def y():
            """y docs"""
            return 1

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

