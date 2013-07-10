__all__ = ['pyeval', 'buildStandardMagicScope']


from pyeval.autoimporter import AutoImporter
from pyeval.magic.scope import MagicScope



def pyeval(expr, *args):
    return eval(expr, {}, buildStandardMagicScope(args))


def buildStandardMagicScope(argStrs):
    autoimporter = AutoImporter()

    scope = MagicScope(autoimporter.proxyImport)

    @scope.registerMagic
    def ai():
        """The AutoImporter instance associate with the MagicScope."""
        return autoimporter

    @scope.registerMagic
    def args():
        """The list of ARG strings after EXPR."""
        return argStrs

    for (i, arg) in enumerate(argStrs):
        def argN(cachedArg=arg):
            """A positional ARG given after EXPR."""
            return cachedArg

        scope.registerMagic(argN, 'a' + str(i))

    return scope


