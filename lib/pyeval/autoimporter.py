__all__ = ['AutoImporter', 'importLast']


from types import ModuleType



def importLast(modpath):
    mod = __import__(modpath)
    for name in modpath.split('.')[1:]:
        mod = getattr(mod, name)
    return mod


class AutoImporter (object):
    def __init__(self, mod):
        assert type(mod) is ModuleType, `mod`

        self._ai_mod = mod

        try:
            path = mod.__file__
        except AttributeError:
            self._ai_path = None
        else:
            if path.endswith('.pyc'):
                path = path[:-1]

            self._ai_path = path


    @property
    def _ai_name(self):
        return self._ai_mod.__name__

    def __repr__(self):
        modrepr = repr(self._ai_mod)
        assert modrepr.startswith('<') and modrepr.endswith('>'), modrepr
        return '<%s for %s>' % (self.__class__.__name__, modrepr[1:-1])

    def __getattr__(self, name):
        try:
            x = getattr(self._ai_mod, name)
        except AttributeError, outerError:
            try:
                x = importLast(self._ai_name + '.' + name)
            except ImportError:
                raise outerError

        if type(x) is ModuleType:
            return AutoImporter(x)
        else:
            return x

