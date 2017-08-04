__all__ = ['AutoImporter']


from types import ModuleType
from weakref import WeakKeyDictionary



class AutoImporter (object):

    class Proxy (object):
        pass # BaseClass exposed so client code can use isinstance(x, AutoImport.Proxy)

    class ModInfo (object):
        def __init__(self, mod):
            self.mod = mod

        @property
        def name(self):
            return self.mod.__name__

        @property
        def path(self):
            try:
                path = self.mod.__file__
            except AttributeError:
                return None
            else:
                if path.endswith('.pyc'):
                    path = path[:-1]

                return path


    def __init__(self):
        self._proxyInfo = WeakKeyDictionary()

    def proxyImport(self, name):

        mod = __import__(name)
        for name in name.split('.')[1:]:
            mod = getattr(mod, name)

        return self._proxyWrap(mod)

    def mod(self, proxy):
        return self._getInfo(proxy).mod

    def name(self, proxy):
        return self._getInfo(proxy).name

    def path(self, proxy):
        return self._getInfo(proxy).path

    # Private:
    def _getInfo(self, proxy):
        if isinstance(proxy, self.Proxy):
            return self._proxyInfo[proxy]
        else:
            raise TypeError('Expected a %s.Proxy; got %r' % (type(self).__name__, proxy))

    def _proxyWrap(self, mod):
        # Bound for the closure of SubProxy to keep SubProxy instances attribute-free:
        ai = self
        modinfo = ai.ModInfo(mod)

        class BoundProxy (ai.Proxy):
            def __repr__(_):
                modrepr = repr(mod)
                assert modrepr.startswith('<') and modrepr.endswith('>'), modrepr
                return '<%s proxy for %s>' % (type(ai).__name__, modrepr[1:-1])

            def __getattribute__(_, name):
                try:
                    x = getattr(mod, name)
                except AttributeError, outerError:
                    try:
                        x = ai.proxyImport(modinfo.name + '.' + name)
                    except ImportError:
                        raise outerError

                if type(x) is ModuleType:
                    return ai._proxyWrap(x)
                else:
                    return x

        proxy = BoundProxy()
        ai._proxyInfo[proxy] = modinfo

        return proxy
