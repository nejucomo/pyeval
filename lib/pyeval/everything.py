__all__ = ['pyeval']


from pyeval.magic.scope import MagicScope



def pyeval(expr, *args):
    scope = MagicScope()
    scope.registerArgsMagic(args)
    return eval(expr, {}, scope)


