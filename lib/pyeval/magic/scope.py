# -*- coding: utf-8 -*-

__all__ = ['MagicScope', 'fallthroughDefault']


import __builtin__
import sys
import pprint
from functools import wraps

from pyeval import display
from pyeval.autoimporter import AutoImporter, importLast
from pyeval.help import HelpBrowser



def fallthroughDefault(key):
    try:
        return AutoImporter(importLast(key))
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

        @self.registerMagicFunction
        def pp(*a, **kw):
            r"""
            An alias to pprint.pprint.  This is useful when you want to explicitly
            see None, which the default display hook elides:

              $ pyeval '{}.get("monkey")'

              $ pyeval 'pp({}.get("monkey"))'
              None
            """
            pprint.pprint(*a, **kw)

        @self.registerMagicFunction
        def p(x):
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

            if type(x) is unicode:
                x = x.encode(display.getEncoding())

            print x

        @self.registerMagicFunction
        def sh(obj):
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


    # Explicit magic interface:
    def registerMagic(self, f, name=None):

        if name is None:
            name = f.__name__

        self.pop(name, None) # Override any previous definitions.
        self._magic[name] = f


    def registerMagicFunction(self, f):

        @wraps(f)
        def magicWrapper():
            return f

        self.registerMagic(magicWrapper)


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
