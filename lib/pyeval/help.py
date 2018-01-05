__all__ = [
    'HelpBrowser',
    ]


import os
import pkg_resources
from pyeval.indentation import dedent, indent


class HelpBrowser (object):

    def __init__(self, scope, delegate=help):
        """The constructor allows dependency injection for unittests."""

        self._scope = scope
        self._ai = scope['ai']
        self._delegate = delegate
        self._topics = {}

        for topicfile in pkg_resources.resource_listdir(__name__, 'doc'):
            if topicfile.endswith('.txt'):
                topicname = topicfile[:-4]
                resource = os.path.join('doc', topicname + '.txt')
                self._topics[topicname] = pkg_resources.resource_string(__name__, resource)

        self._topics['variables'] = self._createVariablesTopic()

        self._topics['topics'] = 'Known topics: %s' % (', '.join(sorted(self._topics.keys())),)

    def getTopics(self):
        return self._topics.keys()

    def getTopicText(self, topicname):
        try:
            topictext = self._topics[topicname]
        except KeyError:
            raise SystemExit('Unknown topic %r; %s' % (
                    topicname,
                    self._topics['topics']))

        header = 'Help Topic: %s' % (topicname,)
        return '%s\n%s\n\n%s\n' % (header, '=' * len(header), topictext)

    def renderTopic(self, topicname):
        print self.getTopicText(topicname)

    def render(self):
        args = self._scope['args']
        if len(args) == 0:
            args = ['intro']
        try:
            [topicname] = args
        except ValueError:
            raise SystemExit('Too many args for help.') # FIXME

        self.renderTopic(topicname)

    _NoArgSentinel = object()
    def __call__(self, obj=_NoArgSentinel):
        if obj is self._NoArgSentinel:
            self.renderTopic('help')
        else:
            if isinstance(obj, self._ai.Proxy):
                obj = self._ai.mod(obj)

            self._delegate(obj)

    def _createVariablesTopic(self):
        return '\n'.join(
            ['%s:\n%s' % (name, indent(dedent(doc)))
             for (name, doc) in self._scope.getMagicDocs()])
