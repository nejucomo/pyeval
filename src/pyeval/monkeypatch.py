__all__ = ['patch']

from contextlib import contextmanager


@contextmanager
def patch(target, attrname, patchvalue):
    saved = getattr(target, attrname)
    setattr(target, attrname, patchvalue)
    try:
        yield
    finally:
        setattr(target, attrname, saved)
