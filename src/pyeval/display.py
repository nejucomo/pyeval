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
    return (getattr(sys.stdout, 'encoding', None)
            or os.environ.get('LC_CTYPE', 'UTF-8').split('.', 1)[-1])
