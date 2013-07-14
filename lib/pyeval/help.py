__all__ = [
    'HelpBrowser',
    'HelpTopic',
    ]


import pkg_resources
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

    HelpText = pkg_resources.resource_string(__name__, 'doc/help.txt')


    @staticmethod
    def _getSubtopics():
        return [
            magicHelp,
            AutoImporterHelp,
            examplesHelp,
            encodingHelp,
            upgradingHelp,
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


class magicHelp (HelpTopic):

    HelpText = pkg_resources.resource_string(__name__, 'doc/magic.txt')


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

    HelpText = pkg_resources.resource_string(__name__, 'doc/AutoImporter.txt')


class examplesHelp (HelpTopic):

    HelpText = pkg_resources.resource_string(__name__, 'doc/examples.txt')



class encodingHelp (HelpTopic):

    HelpText = pkg_resources.resource_string(__name__, 'doc/encoding.txt')


class upgradingHelp (HelpTopic):

    HelpText = pkg_resources.resource_string(__name__, 'doc/upgrading.txt')
