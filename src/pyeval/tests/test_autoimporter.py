import unittest

# These are just used to test importing:
import logging
from logging import handlers

from pyeval.autoimporter import AutoImporter


class AutoImporterTests(unittest.TestCase):
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
        for (proxy, mod) in [(self.parent, logging), (self.child, handlers)]:
            path = self.ai.path(proxy)
            self.assertIsNotNone(path)
            self.assertTrue(path.endswith('.py'), 'Expected .py path, got: %r' % path)
            self.assertEqual(mod.__file__, path)

    def test_pathNone(self):
        self.assertIsNone(self.ai.path(self.ai.proxyImport('sys')))

    def test_pathDotSO(self):
        # Find a C extension module with a .so file
        so_module = None
        for candidate in ['netifaces', '_cffi_backend', 'apt_inst', '_datetime']:
            try:
                mod = __import__(candidate)
                path = getattr(mod, '__file__', None)
                if path and path.endswith('.so'):
                    so_module = candidate
                    break
            except ImportError:
                pass
        if so_module is None:
            self.skipTest('No .so extension module available in this environment')
        self.assertRegex(self.ai.path(self.ai.proxyImport(so_module)), r'\.so$')

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
