import unittest

# These are just used to test importing:
import logging
from logging import handlers

from pyeval.autoimporter import AutoImporter



class AutoImporterTests (unittest.TestCase):
    def setUp(self):
        self.ai = AutoImporter()
        self.parent = self.ai.proxyImport('logging')
        self.child = self.parent.handlers
        self.proxies = [self.parent, self.child]

    def test_proxyInstanceType(self):
        for proxy in self.proxies:
            self.assertIsInstance(proxy, AutoImporter.Proxy)

    def test___repr__(self):
        for proxy in self.proxies:
            r = repr(proxy)
            self.assertNotEqual(-1, r.find('AutoImporter proxy'))

        self.assertNotEqual(-1, repr(self.parent).find('logging'))
        self.assertNotEqual(-1, repr(self.child).find('logging.handlers'))

    def test_mod(self):
        self.assertIs(logging, self.ai.mod(self.parent))
        self.assertIs(handlers, self.ai.mod(self.child))

    def test_name(self):
        self.assertEqual('logging', self.ai.name(self.parent))
        self.assertEqual('logging.handlers', self.ai.name(self.child))

    def test_path(self):
        def getsrc(m):
            path = m.__file__
            assert path.endswith('.pyc')
            return path[:-1]

        self.assertEqual(getsrc(logging), self.ai.path(self.parent))
        self.assertEqual(getsrc(logging.handlers), self.ai.path(self.child))

    def test_pathNone(self):
        self.assertIsNone(self.ai.path(self.ai.proxyImport('sys')))

    def test_pathDotSO(self):
        self.assertRegexpMatches(self.ai.path(self.ai.proxyImport('_struct')), '\.so$')

    def test_nameTypeError(self):
        self.assertRaises(TypeError, self.ai.name, 42)

    def test_attr(self):
        self.assertIs(logging.basicConfig, self.parent.basicConfig)
        self.assertIs(handlers.MemoryHandler, self.child.MemoryHandler)

    def test_attributeTransparency(self):
        for proxy in self.proxies:
            # vars keys are identical:
            self.assertEqual(vars(self.ai.mod(proxy)), vars(proxy))

            # Every attribute of mod, when retrieved through proxy is
            # the same value or a Proxy:
            mod = self.ai.mod(proxy)
            for name in vars(mod).keys():
                value = getattr(mod, name)
                proxied = getattr(proxy, name)
                if not isinstance(proxied, AutoImporter.Proxy):
                    self.assertIs(value, proxied,
                                  'Attribute %r: %r is not %r' % (name, proxied, value))

    def test_AttributeError(self):
        for proxy in self.proxies:
            try:
                self.assertRaises(AttributeError, getattr, proxy, 'WOMBATS!')
            except ImportError:
                self.fail('A missing attribute on an AutoImporter resulted in an ImportError.')


