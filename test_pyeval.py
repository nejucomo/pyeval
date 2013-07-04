#! /usr/bin/env python

import sys
import unittest
from types import ModuleType
import pprint
from cStringIO import StringIO
import math
import re

import pyeval



class mainTests (unittest.TestCase):

    def _test_main(self, expected, args):
        displays = []
        pyeval.main(args, displays.append)
        self.assertEqual([expected], displays)

    def test_a1(self):
        self._test_main('B', ['a1', 'A', 'B', 'C'])

    def test_42(self):
        self._test_main(42, ['42', 'A', 'B', 'C'])

    def test_math_pi(self):
        self._test_main(math.pi, ['math.pi', 'A', 'B', 'C'])



class DocTests (unittest.TestCase):

    IndentRgx = re.compile(r'^    .*?$', re.MULTILINE)
    InvocationRgx = re.compile(r"^    \$ (echo '(?P<INPUT>.*?)' \| )?pyeval '(?P<EXPR>.*?)' ?(?P<ARGS>.*?)$")


    def _parseEntries(self, text):
        entry = None
        for m in self.IndentRgx.finditer(text):
            match = m.group(0)
            m2 = self.InvocationRgx.match(match)
            if m2 is None:
                entry[3].append(m.group(0).lstrip())
            else:
                if entry is not None:
                    yield entry

                args = m2.group('ARGS').split()
                entry = (m2.group('EXPR'), args, m2.group('INPUT'), [])

        if entry is not None:
            yield entry


    def test_docs(self):

        hb = pyeval.HelpBrowser(pyeval.MagicScope())

        for (topicname, topic) in [('help', hb)] + hb.topicsdict.items():
            for (expr, args, inputText, outlines) in self._parseEntries(repr(topic)):
                try:
                    if inputText is None:
                        inputText = ''

                    expectedOut = '\n'.join(outlines) + '\n'

                    # Implement wildcard matches on "...":
                    expectedPattern = re.escape(expectedOut)
                    expectedRgx = re.compile(expectedPattern.replace(r'\.\.\.', '.*?'))

                    fio = FakeIO(inputText + '\n')

                    with fio:
                        pyeval.main([expr] + args)

                    self.assertRegexpMatches(fio.fakeout.getvalue(), expectedRgx)
                    self.assertEqual('', fio.fakeerr.getvalue())

                except Exception, e:
                    e.args += ('In topic %r' % (topicname,),
                               'In EXPR %r' % (expr,),
                               )
                    raise



class pyevalTests (unittest.TestCase):
    """High-level tests of pyeval.pyeval."""

    def test_autoimportTopLevel(self):
        import math
        self.assertIs(math, pyeval.pyeval('math')._ai_mod)

    def test_autoimportSubmodule(self):
        ai = pyeval.pyeval('faketestpackage.faketestmodule')
        self.assertIs(ModuleType, type(ai._ai_mod))



class displayPrettyTests (unittest.TestCase):
    """displayPretty should behave like standard sys.displayhook, except pformat is used."""

    def test_displayNone(self):
        fio = FakeIO()

        with fio:
            pyeval.displayPretty(None)

        self.assertEqual('', fio.fakeout.getvalue())
        self.assertEqual('', fio.fakeerr.getvalue())

    def test_displayValues(self):
        for value in [42, "banana", range(1024), vars()]:
            f = StringIO()
            pprint.pprint(value, f)
            expected = f.getvalue()

            fio = FakeIO()

            with fio:
                pyeval.displayPretty(value)

            self.assertEqual(expected, fio.fakeout.getvalue())
            self.assertEqual('', fio.fakeerr.getvalue())



class MagicScopeTests (unittest.TestCase):
    def setUp(self):
        self.caught = []
        self.scope = pyeval.MagicScope(self.caught.append)

        self.args = [self.a0, self.a1] = ['foo', 'bar']
        self.scope.registerArgsMagic(self.args)

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
                self.assertIsInstance(self.scope['help'], pyeval.HelpBrowser)
                self.assertEqual(pprint.pformat, self.scope['pf'])
                self.assertEqual(self.args, self.scope['args'])
                self.assertEqual(self.a0, self.scope['a0'])
                self.assertEqual(self.a1, self.scope['a1'])

    def test_fallthrough(self):
        key = '6ff25ffc'
        x = self.scope[key]
        self.assertIsNone(x)
        self.assertEqual([key], self.caught)

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



class AutoImporterTests (unittest.TestCase):
    def setUp(self):
        import logging
        self.logging = logging
        from logging import handlers
        self.handlers = handlers

        self.parent = pyeval.AutoImporter(pyeval.import_last('logging'))
        self.child = self.parent.handlers

    def test___repr__(self):
        r = repr(self.child)
        self.assertNotEqual(-1, r.find('AutoImporter'))
        self.assertNotEqual(-1, r.find('logging.handlers'))

    def test__ai_mod(self):
        self.assertIs(self.logging, self.parent._ai_mod)
        self.assertIs(self.handlers, self.child._ai_mod)

    def test__ai_name(self):
        self.assertEqual('logging', self.parent._ai_name)
        self.assertEqual('logging.handlers', self.child._ai_name)

    def test__ai_path(self):
        def getsrc(m):
            path = m.__file__
            assert path.endswith('.pyc')
            return path[:-1]

        self.assertEqual(getsrc(self.logging), self.parent._ai_path)
        self.assertEqual(getsrc(self.logging.handlers), self.child._ai_path)

    def test_attr(self):
        self.assertIs(self.logging.basicConfig, self.parent.basicConfig)
        self.assertIs(self.handlers.MemoryHandler, self.child.MemoryHandler)



class HelpBrowserTests (unittest.TestCase):
    def setUp(self):
        self.delegateCalls = []
        self.help = pyeval.HelpBrowser(pyeval.MagicScope(), self.delegateCalls.append)

    def test___repr__(self):
        self.assertEqual(pyeval.Usage, repr(self.help))
        self.assertEqual([], self.delegateCalls)

    def test_autoImporter(self):
        magic = pyeval.MagicScope()
        ai = magic['sys']
        self.assertIsInstance(ai, pyeval.AutoImporter)
        self.help(ai)
        self.assertEqual([sys], self.delegateCalls)




class FakeIO (object):
    def __init__(self, inbytes=''):
        self.inbytes = inbytes

    def __enter__(self):
        self.realout = sys.stdout
        self.realerr = sys.stderr
        self.realin = sys.stdin

        self.fakeout = sys.stdout = StringIO()
        self.fakeerr = sys.stderr = StringIO()
        self.fakein = sys.stdin = StringIO(self.inbytes)

        return self

    def __exit__(self, *a):
        sys.stdout = self.realout
        sys.stderr = self.realerr
        sys.stdin = self.realin



if __name__ == '__main__':
    unittest.main()
