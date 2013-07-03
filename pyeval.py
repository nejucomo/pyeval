CopyrightInfo = '''
Copyright 2010 Nathan Wilcox

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
'''

Usage = '''
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

For more help topics, run:

  $ pyeval 'help.topics'
  ...

'''

MagicScopeText = '''
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

Magic variables have individual help documentation, see:

  $ pyeval 'help.magic'
  ...

'''

MagicVariablesTemplate = '''
For detail on the MagicScope, run:

  $ pyeval 'help.MagicScope'
  ...

Magic Variables:

%(MAGIC_VARS_HELP)s
'''

AutoImporterText = '''
The AutoImporter class allows expressions to use modules directly with
an implicit "import on demand" functionality.

Unfortunately the implementation is not completely transparent:
references to what look like python modules are actually to an instance
of AutoImporter which proxies attribute access to the module.

You can see this by inspecting the repr of a module expression:

  $ pyeval 'logging.config'
  FIXME

'''

ExamplesText = '''
FIXME - write this
'''


import __builtin__
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



class MagicScope (dict):
    def __init__(self, fallthrough=lambda key: AutoImporter(import_last(key))):

        self._fallthrough = fallthrough
        self._magic = {}

        dict.__init__(self, vars(__builtin__))

        # Standard magic:
        @self.registerMagic
        def help():
            """The help browser."""
            return HelpBrowser(self)

        @self.registerMagic
        def ri():
            """The raw standard input as a string.  The first access calls sys.stdin.read()"""
            return sys.stdin.read()

        @self.registerMagic
        def i():
            """The stripped standard input string.  Defined as 'ri.strip()'"""
            return self['ri'].strip()

        @self.registerMagic
        def rlines():
            """The list of raw standard input lines.  Defined as 'ri.split("\\n")'"""
            return self['ri'].split('\n')

        @self.registerMagic
        def lines():
            """The list of stripped standard input lines.  Defined as '[ l.strip() for l in self['rlines'] ]'"""
            return [ l.strip() for l in self['rlines'] ]

        @self.registerMagic
        def pf():
            """An alias to pprint.pformat."""
            return pprint.pformat


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
    def __init__(self, mod, parent=None):
        assert type(mod) is ModuleType, `mod`

        self._ai_mod = mod
        self._ai_parent = parent

        try:
            path = mod.__file__
        except AttributeError:
            self._ai_path = None
        else:
            if path.endswith('.pyc'):
                path = path[:-1]

            self._ai_path = path


    @property
    def _ai_fullname(self):
        return self._ai_mod.__name__

    def __repr__(self):
        return '<%s@%016x %r>' % (self.__class__.__name__, id(self), self._ai_mod)

    def __getattr__(self, name):
        try:
            x = getattr(self._ai_mod, name)
        except AttributeError:
            x = import_last(self._ai_fullname + '.' + name)

        if type(x) is ModuleType:
            return AutoImporter(x, self)
        else:
            return x



class HelpTopic (object):
    def __init__(self, repr):
        self._repr = repr

    def __repr__(self):
        return self._repr



class HelpBrowser (HelpTopic):

    def __init__(self, scope, delegate=help):
        """The constructor allows dependency injection for unittests."""
        HelpTopic.__init__(self, Usage)

        self._delegate = delegate

        self.topicsdict = {
            'MagicScope': HelpTopic(MagicScopeText),
            'AutoImporter': HelpTopic(AutoImporterText),
            'examples': HelpTopic(ExamplesText),
            }

        magiclist = [ '%s\n- %s' % t for t in scope.getMagicDocs() ]
        self.topicsdict['magic'] = HelpTopic(
            MagicVariablesTemplate % {
                'MAGIC_VARS_HELP': '\n\n'.join(magiclist),
                })

        # Meta Topics is a list of Topics:
        topickeys = sorted(self.topicsdict.keys())
        topicnames = [ '* help.%s' % (n,) for n in topickeys ]
        topicnames.insert(0, '* help')
        topics = '\n'.join(topicnames)

        self.topicsdict['topics'] = HelpTopic('\nTopics:\n\n%s\n\n' % (topics,))

        for (name, topic) in self.topicsdict.iteritems():
            setattr(self, name, topic)


    def __call__(self, obj):
        if isinstance(obj, AutoImporter):
            obj = obj._ai_mod

        self._delegate(obj)


