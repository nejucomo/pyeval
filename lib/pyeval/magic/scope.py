__all__ = ['MagicScope']


from functools import wraps



class MagicScope (dict):
    def __init__(self, fallthrough):
        assert callable(fallthrough)

        self._fallthrough = fallthrough
        self._magic = {}


    # Explicit magic interface:
    def registerMagic(self, f, name=None):

        if name is None:
            name = f.__name__

        self.pop(name, None) # Override any previous definitions.
        self._magic[name] = f


    def registerMagicFunction(self, f):

        @wraps(f)
        def magicWrapper(scope):
            @wraps(f)
            def wrapped(*a, **kw):
                return f(scope, *a, **kw)
            return wrapped

        self.registerMagic(magicWrapper)


    def getMagicDocs(self):
        return sorted( [ (k, f.__doc__) for (k, f) in self._magic.iteritems() ] )


    # dict interface:
    def __repr__(self):
        # Explicitly override dict.__repr__ to prevent evaluating magic values:
        return '<%s %r>' % (type(self).__name__, sorted(self.keys()))


    def __getitem__(self, key):
        method = self._magic.get(key)

        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if method is None:
                try:
                    return self._fallthrough(key)
                except Exception: # Dangerous!
                    raise NameError(key)
            else:
                value = self[key] = method(self)
                return value


    def __len__(self):
        return len(self.keys())


    def iterkeys(self):
        visited = set()

        for key in self._magic.iterkeys():
            visited.add(key)
            yield key

        for key in dict.iterkeys(self):
            if key not in visited:
                yield key

    def iteritems(self):
        return ( (k, self[k]) for k in self.iterkeys() )

    def itervalues(self):
        return ( v for (k, v) in self.iteritems() )

    def keys(self):
        return list(self.iterkeys())

    def items(self):
        return list(self.iteritems())

    def values(self):
        return list(self.itervalues())
