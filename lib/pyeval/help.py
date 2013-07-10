__all__ = [
    'AutoImporterHelp',
    'HelpBrowser',
    'HelpTopic',
    'MagicScopeHelp',
    'encodingHelp',
    'examplesHelp',
    'variablesHelp',
    ]


from pyeval.indentation import dedent, indent


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

    HelpText = r"""
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
        self._ai = scope['ai']
        self._delegate = delegate

        HelpTopic.__init__(self, None)

    @property
    def name(self):
        return 'help'

    @property
    def fullname(self):
        return self.name

    def __call__(self, obj):
        if isinstance(obj, self._ai.Proxy):
            obj = self._ai.mod(obj)

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

      It accomplishes this by constructing a proxy object to an underlying
      python module which delegates attribute lookups to that module.
      For example, this works:

          $ pyeval 'math.pi'
          3.141592653589793

      If any attribute lookup fails, the proxy attempts to use
      the AutoImporter to proxy a submodule, and if that fails, an
      AttributeError is raised.

      Unfortunately this approach is not completely transparent: references to
      what look like python modules are actually to an instance of
      AutoImporter.Proxy which proxies attribute access to the module.

      You can see this by inspecting the repr of a module expression:

          $ pyeval 'logging.config'
          <AutoImporter proxy for module '...config...'>

      The AutoImporter class provides methods to lookup information
      about the original module from a proxy.  Compare the following
      example to the previous:

          $ pyeval 'ai.mod(logging.config)'
          <module '...config...'>

      For more details on these methods, run:

          $ pyeval 'help(ai)'
    """


class examplesHelp (HelpTopic):

    HelpText = r"""
      Exploring python modules:

          $ pyeval 'help(logging)'
          ...

          $ pyeval 'help(logging.handlers.MemoryHandler)'
          ...

      Finding the path to a module:

          $ pyeval 'ai.path(logging.handlers)'
          '/.../handlers.py'

      Viewing the source of a module:

          $ view $(pyeval 'p(ai.path(logging.handlers))')

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
