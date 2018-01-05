__all__ = ['displayPretty', 'getEncoding']

import pprint
import sys
import os

from pyeval.help import HelpBrowser


def displayPretty(obj):
    if obj is not None:
        if isinstance(obj, HelpBrowser):
            obj.render()
        else:
            pprint.pprint(obj)


def getEncoding():
    # NOTE: I do not know how well this will work in practice:
    # If sys.stdout.encoding is not set (because stdout is not a terminal),
    # we use LC_CTYPE *anyway*.
    return (getattr(sys.stdout, 'encoding', None)
            or os.environ.get('LC_CTYPE', 'UTF-8').split( '.', 1 )[-1])
