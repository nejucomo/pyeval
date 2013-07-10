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
