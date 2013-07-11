__all__ = ['pyeval', 'pyevalAndDisplay', 'buildStandardMagicScope']


import __builtin__
import sys

from pyeval.autoimporter import AutoImporter
from pyeval.display import displayPretty
from pyeval.magic.scope import MagicScope
from pyeval.magic import variables, functions



def pyevalAndDisplay(expr, *args, **kw):
    sys.displayhook = kw.pop('displayhook', displayPretty)

    if len(kw) > 0:
        raise TypeError('pyevalAndDisplay() got unexpected keywords: %r' % (kw.keys(),))

    result = pyeval(expr, *args)
    sys.displayhook(result)


def pyeval(expr, *args):
    return eval(expr, {}, buildStandardMagicScope(args))


def buildStandardMagicScope(argStrs, autoimporter=None):
    if autoimporter is None:
        autoimporter = AutoImporter()

    scope = MagicScope(autoimporter.proxyImport)
    scope.update(vars(__builtin__))

    @scope.registerMagic
    def ai(_):
        """The AutoImporter instance associate with the MagicScope."""
        return autoimporter

    @scope.registerMagic
    def args(_):
        """The list of ARG strings after EXPR."""
        return argStrs

    for (i, arg) in enumerate(argStrs):
        def argN(_, cachedArg=arg):
            """A positional ARG given after EXPR."""
            return cachedArg

        scope.registerMagic(argN, 'a' + str(i))

    for name in variables.__all__:
        scope.registerMagic(getattr(variables, name))

    for name in functions.__all__:
        scope.registerMagicFunction(getattr(functions, name))

    return scope


