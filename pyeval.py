# -*- coding: utf-8 -*-

CopyrightInfo = r"""
Copyright 2013 Nathan Wilcox

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

Usage = r"""
Usage: pyeval EXPR [ARG...]

Evaluate EXPR with the python interpreter.  Any other ARGs are available
as strings in the expression.  Example:

    $ pyeval 'math.cos(math.pi * 2)'
    1.0

Evaluation differs from the interactive interpreter in three ways:
result display, magic variables, and automatic imports.

The result is displayed with pprint.pprint, unless it is None, in which case
nothing is displayed.

There are "magic variables" whose result is only computed on the first
dereference. For more detail, run:

    $ pyeval 'help.MagicScope'
    ...

Any reference which is not a standard builtin or a magic variable results
in an AutoImporter instance, which the first example demonstrates by
importing 'math'.  For more detail, run:

    $ pyeval 'help.AutoImporter'
    ...

For more examples, run:

    $ pyeval 'help.examples'
    ...
"""


import __builtin__
import os
import sys
import pprint
from types import ModuleType



def displayPretty(obj):
    if obj is not None:
        pprint.pprint(obj)


def main(args = sys.argv[1:], displayhook=displayPretty):
    sys.displayhook = displayhook

    expr, strs = args[0], args[1:]
    result = pyeval(expr, *strs)
    sys.displayhook(result)


def pyeval(expr, *args):
    scope = MagicScope()
    scope.registerArgsMagic(args)
    return eval(expr, {}, scope)


def import_last(modpath):
    mod = __import__(modpath)
    for name in modpath.split('.')[1:]:
        mod = getattr(mod, name)
    return mod


def getEncoding():
    # NOTE: I do not know how well this will work in practice:
    # If sys.stdout.encoding is not set (because stdout is not a terminal),
    # we use LC_CTYPE *anyway*.
    return (getattr(sys.stdout, 'encoding', None)
            or os.environ.get('LC_CTYPE', 'UTF-8').split( '.', 1 )[-1])


def dedent(text):
    indentedlines = text.rstrip().split('\n')

    while indentedlines[0] == '':
        indentedlines.pop(0)

    firstline = indentedlines[0]

    indent = len(firstline) - len(firstline.lstrip())

    dedentedlines = []
    for indented in indentedlines:
        assert indented == '' or indented[:indent].strip() == '', `indented`
        dedentedlines.append(indented[indent:])

    return '\n'.join(dedentedlines) + '\n'


def indent(text, amount=2):
    indent = ' ' * amount
    separator = '\n' + indent
    return indent + separator.join(text.rstrip().split('\n')) + '\n'


def fallthroughDefault(key):
    try:
        return AutoImporter(import_last(key))
    except ImportError:
        raise NameError(key)



class MagicScope (dict):
    def __init__(self, fallthrough=fallthroughDefault):

        self._fallthrough = fallthrough
        self._magic = {}

        dict.__init__(self, vars(__builtin__))

        # Standard magic:
        @self.registerMagic
        def help():
            r"""The help browser."""
            return HelpBrowser(self)

        @self.registerMagic
        def ri():
            r"""
              The raw standard input as a string.  The first access calls
              'sys.stdin.read()', so compare these:

                $ echo 'foo' | pyeval 'len(sys.stdin.read())'
                4

                $ echo 'foo' | pyeval 'len(ri)'
                4

              Notice because of magic variable caching, using 'ri' multiple times
              always results in the same input:

                $ echo 'foo' | pyeval '[len(ri), ri.replace("o", "-")]'
                [4, 'f--\n']
            """
            return sys.stdin.read()

        @self.registerMagic
        def i():
            r"""
            The stripped standard input string.  Defined as 'ri.strip()' so:

              $ echo 'foo' | pyeval 'len(ri.strip())'
              3

              $ echo 'foo' | pyeval 'len(i)'
              3
            """
            return self['ri'].strip()

        @self.registerMagic
        def rlines():
            r"""
            The list of raw standard input lines.  Defined as 'ri.split("\\n")'.
            """
            return self['ri'].split('\n')

        @self.registerMagic
        def lines():
            r"""
            The list of stripped standard input lines.  Defined as:
            '[ l.strip() for l in self['rlines'] ]'
            """
            return [ l.strip() for l in self['rlines'] ]

        @self.registerMagic
        def ilines():
            r"""
            A line iterator over stripped lines from stdin.  Defined as:
            '( l.strip() for l in sys.stdin )'
            """
            return ( l.strip() for l in sys.stdin )

        @self.registerMagic
        def pp():
            r"""
            An alias to pprint.pprint.  This is useful when you want to explicitly
            see None, which the default display hook elides:

              $ pyeval '{}.get("monkey")'

              $ pyeval 'pp({}.get("monkey"))'
              None
            """
            return pprint.pprint

        @self.registerMagic
        def p():
            r"""
            A wrapper around the print statement.  Use this if you want
            to avoid pretty printed results:

              $ pyeval 'p({}.get("nothing"))'
              None

              $ pyeval 'range(123)'
              [0,
               1,
               ...

              $ pyeval 'p(range(123))'
              [0, 1, ...

            Also, it allows you to print strings directly:

              $ pyeval 'p("x\ty\nz")'
              x	y
              z

            Note, it's possible to display unicode this way, using the detected encoding:

              $ pyeval 'p(u"\u2606")'
              ☆

            For more details on the encoding, run:

              $ pyeval 'help.encoding'
              ...
            """

            def printFunc(x):
                r"""print the argument."""
                if type(x) is unicode:
                    x = x.encode(getEncoding())

                print x

            return printFunc

        @self.registerMagic
        def sh():
            r"""
            Display the argument in a "shell friendly manner":

            1. If obj is None, display nothing.

            2. If obj is not iterable, treat it as [obj] in the following steps:

            For each item in the iterable:

            3. Convert the item to unicode as: unicode(item)

            4. Print the result with p().

            NOTE: This was the default display behavior of pyeval <=
            2.1.6, so to produce the equivalent output in pyeval > 2.1.6,
            wrap the expression in 'sh(...)'.

            An example of emulating grep

              $ echo -e 'food\nmonkey\nfool' | grep '^foo'
              food
              fool

              $ echo -e 'food\nmonkey\nfool' | pyeval 'sh( l for l in ilines if l.startswith("foo") )'
              food
              fool
            """
            def sh(obj):
                if obj is None:
                    return

                it = [obj]
                if type(obj) not in (str, unicode):
                    try:
                        it = iter(obj)
                    except TypeError:
                        pass

                for elem in it:
                    self['p'](unicode(elem))

            return sh


    # Explicit magic interface:
    def registerMagic(self, f, name=None):

        if name is None:
            name = f.__name__

        self.pop(name, None) # Override any previous definitions.
        self._magic[name] = f


    def registerArgsMagic(self, argStrs):
        @self.registerMagic
        def args():
            """The list of ARG strings after EXPR."""
            return argStrs

        for (i, arg) in enumerate(argStrs):
            def argN(cachedArg=arg):
                """A positional ARG given after EXPR."""
                return cachedArg

            self.registerMagic(argN, 'a' + str(i))


    def getMagicDocs(self):
        return sorted( [ (k, f.__doc__) for (k, f) in self._magic.iteritems() ] )


    # Scope interface:
    def __getitem__(self, key):
        method = self._magic.get(key)

        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if method is None:
                return self._fallthrough(key)
            else:
                value = self[key] = method()
                return value



class AutoImporter (object):
    def __init__(self, mod):
        assert type(mod) is ModuleType, `mod`

        self._ai_mod = mod

        try:
            path = mod.__file__
        except AttributeError:
            self._ai_path = None
        else:
            if path.endswith('.pyc'):
                path = path[:-1]

            self._ai_path = path


    @property
    def _ai_name(self):
        return self._ai_mod.__name__

    def __repr__(self):
        modrepr = repr(self._ai_mod)
        assert modrepr.startswith('<') and modrepr.endswith('>'), modrepr
        return '<%s for %s>' % (self.__class__.__name__, modrepr[1:-1])

    def __getattr__(self, name):
        try:
            x = getattr(self._ai_mod, name)
        except AttributeError:
            x = import_last(self._ai_name + '.' + name)

        if type(x) is ModuleType:
            return AutoImporter(x)
        else:
            return x



class HelpTopic (object):

    def __init__(self, parent):
        self.parent = parent
        self.subtopics = {}

        for topicCls in self._getSubtopics():
            topic = topicCls(self)
            self.subtopics[topic.name] = topic

    # Subclass interface:
    @staticmethod
    def _getSubtopics():
        return []

    # User interface:
    @property
    def name(self):
        cname = type(self).__name__
        assert cname.endswith('Help'), `self`
        return cname[:-len('Help')]

    @property
    def fullname(self):
        return '%s.%s' % (self.parent.fullname, self.name)

    def getAllSubtopics(self):
        topics = [self]

        for (_, topic) in sorted(self.subtopics.items()):
            topics.extend(topic.getAllSubtopics())

        return topics

    def __getattr__(self, name):
        return self.subtopics[name]

    def __repr__(self):
        text = dedent("""
          Topic: %(NAME)s

          %(BODY)s
        """) % {
            'NAME': self.fullname,
            'BODY': dedent(self.HelpText),
            }

        if len(self.subtopics) > 0:
            subnames = [t.fullname for t in self.getAllSubtopics()]
            subnames.pop(0)
            subtopics = '\n'.join(sorted(subnames))

            text = dedent("""
              %(PREFIX)s\

              Subtopics:
              %(SUBTOPICS)s
            """) % {
                'PREFIX': text,
                'SUBTOPICS': subtopics,
                }

        return text


class HelpBrowser (HelpTopic):

    HelpText = Usage

    @staticmethod
    def _getSubtopics():
        return [
            MagicScopeHelp,
            AutoImporterHelp,
            examplesHelp,
            encodingHelp,
            ]


    def __init__(self, scope, delegate=help):
        """The constructor allows dependency injection for unittests."""

        self._scope = scope
        self._delegate = delegate

        HelpTopic.__init__(self, None)

    @property
    def name(self):
        return 'help'

    @property
    def fullname(self):
        return self.name

    def __call__(self, obj):
        if isinstance(obj, AutoImporter):
            obj = obj._ai_mod

        self._delegate(obj)


class MagicScopeHelp (HelpTopic):

    HelpText = r"""
      The global scope of EXPR is an instance of MagicScope, a subclass of
      dict, which:

      * includes all __builtins__.
      * includes magic variables (see below).
      * resolves to an AutoImporter for any unbound reference.

      For more detail about the AutoImporter mechanism, run:

          $ pyeval 'help.AutoImporter'
          ...

      A magic variable's value is only computed on the first reference.
      For example, the magic variable 'i' is the string read from sys.stdin.
      It can be used idempotently with multiple references in a single
      expression.  This example shows the number of characters and words
      in stdin:

          $ echo 'Hello World!' | pyeval '[len(i), len(i.split())]'
          [12, 2]
    """

    @staticmethod
    def _getSubtopics():
        return [variablesHelp]


class variablesHelp (HelpTopic):

    @property
    def HelpText(self):
        scope = self.parent.parent._scope

        return '\n'.join(
            ['%s:\n%s' % (name, indent(dedent(doc)))
             for (name, doc) in scope.getMagicDocs()])


class AutoImporterHelp (HelpTopic):

    HelpText = r"""
      The AutoImporter class allows expressions to use modules directly with
      an implicit "import on demand" functionality.

      It accomplishes this by acting as a proxy to an underlying python module,
      and delegating attribute lookups to that module.  For example, this works:

          $ pyeval 'math.pi'
          3.141592653589793

      If any attribute lookup fails, it attempts to import a submodule, and
      if that is successful, it wraps that submodule in a new AutoImporter.

      Unfortunately this approach is not completely transparent: references to
      what look like python modules are actually to an instance of AutoImporter
      which proxies attribute access to the module.

      You can see this by inspecting the repr of a module expression:

          $ pyeval 'logging.config'
          <AutoImporter for module '...'>

      An AutoImporter instance has the following attributes:

      _ai_mod
        The original module which is being proxied.

      _ai_path
        A path string to the source of the module.  This is useful for testing
        your PYTHONPATH:

          $ pyeval 'pyeval._ai_path'
          '/.../pyeval.py'

      _ai_name
        The full module name of the module.  For example:

          $ pyeval 'logging.config._ai_name'
          'logging.config'

      The 'help' HelpBrowser is aware of AutoImporters, so pyeval can be used
      similar to pydoc:

          $ pyeval 'help(logging)'
          ...

          $ pydoc 'logging'
          ...
    """


class examplesHelp (HelpTopic):

    HelpText = r"""
      Exploring python modules:

          $ pyeval 'help(logging)'
          ...

          $ pyeval 'help(logging.handlers.MemoryHandler)'
          ...

      Finding the path to a module:

          $ pyeval 'logging.handlers._ai_path'
          '/.../handlers.py'

      Viewing the source of a module:

          $ view $(pyeval 'p(logging.handlers._ai_path)')

      Pretty printing sys.path:

          $ pyeval 'sys.path'
          ...

      Assigning and using the python version string to a shell variable:

          $ PYVER=$(pyeval 'p("%d.%d" % sys.version_info[:2])')
          $ ls /usr/lib/python${PYVER} | wc -l
    """


class encodingHelp (HelpTopic):

    HelpText = r"""
      The p() magic function encodes unicode arguments using an encoding
      selected in this order, where the first defined value is used:

      1. sys.stdout.encoding
      2. The substring of the LC_CTYPE environment variable after the rightmost '.'
      3. UTF-8

      The first works when the stdout is connected to a terminal. When stdout
      is not connected to a terminal, such as when pyeval is used in a shell
      pipeline, the second will hopefully choose the user's preferred encoding.

      There is a potential for LC_CTYPE to be a valid setting for the user's
      locale, but to be invalid as a python encoding specifier.

      Several other display functions, such as sh() rely on p().
    """
