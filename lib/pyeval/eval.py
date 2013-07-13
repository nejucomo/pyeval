__all__ = ['pyeval', 'pyevalAndDisplay', 'buildStandardMagicScope']


import __builtin__
import sys

from pyeval.autoimporter import AutoImporter
from pyeval.display import displayPretty
from pyeval.magic.scope import MagicScope
from pyeval.magic import variables, functions
from pyeval.monkeypatch import patch



def pyevalAndDisplay(expr, *args, **kw):
    """
    Evaluate expr and args, then display the result with sys.displayhook.

    If the displayhook keyword is given and None, sys.displayhook is not
    modified.  Otherwise it is temporarily assigned to sys.displayhook
    and restored before returning.  It not given, it defaults to
    pyeval.display.displayPretty.
    """
    displayhook = kw.pop('displayhook', displayPretty)
    if len(kw) > 0:
        raise TypeError('pyevalAndDisplay() got unexpected keywords: %r' % (kw.keys(),))

    if displayhook is None:
        displayhook = sys.displayhook

    with patch(sys, 'displayhook', displayhook):
        result = pyeval(expr, *args)
        sys.displayhook(result)


def pyeval(expr, *args):
    return eval(expr, {}, buildStandardMagicScope(args))


def buildStandardMagicScope(argStrs, autoimporter=None):
    if autoimporter is None:
        autoimporter = AutoImporter()

    def fallthrough(key):
        try:
            return getattr(__builtin__, key)
        except AttributeError:
            return autoimporter.proxyImport(key)

    scope = MagicScope(fallthrough)

    @scope.registerMagic
    def ai(_):
        """The AutoImporter instance associate with the MagicScope."""
        return autoimporter

    scope.registerMagicConstant(
        argStrs,
        'args',
        'The list of ARG strings after EXPR, which is: %r' % (argStrs,))

    for (i, arg) in enumerate(argStrs):
        scope.registerMagicConstant(
            arg,
            'a%d' % (i,),
            'The %d-th positional ARG given after EXPR, which is: %r' % (i, arg))

    for name in variables.__all__:
        scope.registerMagic(getattr(variables, name))

    for name in functions.__all__:
        scope.registerMagicFunction(getattr(functions, name))

    return scope


