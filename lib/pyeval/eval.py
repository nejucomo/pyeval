__all__ = ['pyeval', 'buildStandardMagicScope']


from pyeval.autoimporter import AutoImporter
from pyeval.magic.scope import MagicScope



def pyeval(expr, *args):
    return eval(expr, {}, buildStandardMagicScope(args))


def buildStandardMagicScope(args):
    autoimporter = AutoImporter()
    scope = MagicScope(autoimporter.proxyImport)

    @scope.registerMagic
    def ai():
        """The AutoImporter instance associate with the MagicScope."""
        return autoimporter

    scope.registerArgsMagic(args)

    return scope


