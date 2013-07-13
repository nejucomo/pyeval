import sys
import re
import unittest
import traceback

from pyeval.autoimporter import AutoImporter
from pyeval.eval import buildStandardMagicScope
from pyeval.help import HelpBrowser
from pyeval.indentation import dedent
from pyeval.main import main
from pyeval.tests.fakeio import FakeIO



class HelpBrowserTests (unittest.TestCase):
    def setUp(self):
        self.delegateCalls = []
        self.help = HelpBrowser(buildStandardMagicScope([]), self.delegateCalls.append)

    def test___repr__(self):
        self.assertNotEqual(-1, repr(self.help).find(dedent(self.help.HelpText)))
        self.assertEqual([], self.delegateCalls)

    def test_autoImporter(self):
        proxy = self.help._scope['sys']
        self.assertIsInstance(proxy, AutoImporter.Proxy)
        self.help(proxy)
        self.assertEqual([sys], self.delegateCalls)



class DocExampleVerificationTests (unittest.TestCase):

    IndentRgx = re.compile(r'^    .*?$', re.MULTILINE)
    InvocationRgx = re.compile(r"^    \$")
    PyevalInvocationRgx = re.compile(
        r"^    \$ (echo (?P<EFLAG>-e )?'(?P<INPUT>.*?)' \| )?pyeval '(?P<EXPR>.*?)' ?(?P<ARGS>.*?)$")


    def _parseEntries(self, text):
        entry = None
        for m in self.IndentRgx.finditer(text):
            match = m.group(0)
            m2 = self.InvocationRgx.match(match)
            if m2 is None:
                entry[3].append(m.group(0)[4:])
            else:
                if entry is not None and entry[0] is not None:
                    yield entry

                m3 = self.PyevalInvocationRgx.match(match)
                if m3 is not None:
                    args = m3.group('ARGS').split()
                    teststdin = m3.group('INPUT')
                    if teststdin is not None:
                        if m3.group('EFLAG') is not None:
                            teststdin = teststdin.replace('\\n', '\n')
                    entry = (m3.group('EXPR'), args, teststdin, [])
                else:
                    # This is an non-tested example, such as a non-call to pyeval.
                    entry = (None, None, None, [])

        if entry is not None and entry[0] is not None:
            yield entry


    def test_docs(self):

        hb = HelpBrowser(buildStandardMagicScope([]))

        count = 0

        for topic in hb.getAllSubtopics():
            for (expr, args, inputText, outlines) in self._parseEntries(repr(topic)):
                count += 1
                try:
                    if inputText is None:
                        inputText = ''

                    expectedOut = '\n'.join(outlines)

                    # Implement wildcard matches on "...":
                    expectedRawPattern = re.escape(expectedOut)
                    expectedPattern = expectedRawPattern.replace(r'\.\.\.', '.*?')
                    expectedRgx = re.compile(expectedPattern, re.DOTALL)

                    fio = FakeIO(inputText + '\n')

                    with fio:
                        try:
                            main([expr] + args)
                        except Exception:
                            traceback.print_exc(file=fio.fakeerr)

                    if expectedOut.startswith('Traceback (most recent call last)'):
                        fio.checkRegexp(self, '^$', expectedRgx)
                    else:
                        fio.checkRegexp(self, expectedRgx, '^$')

                except Exception, e:
                    e.args += ('In topic %r' % (topic.fullname,),
                               'In EXPR %r' % (expr,),
                               )
                    raise
