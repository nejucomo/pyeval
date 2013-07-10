__all__ = ['pyeval', 'buildStandardMagicScope']


import __builtin__

from pyeval.autoimporter import AutoImporter
from pyeval.magic.scope import MagicScope
from pyeval.magic import variables, functions



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


