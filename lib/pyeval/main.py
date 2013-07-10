__all__ = ['main']

import sys

from pyeval.display import displayPretty
from pyeval.eval import pyeval


def main(args = sys.argv[1:], displayhook=displayPretty):
    sys.displayhook = displayhook

    expr, strs = args[0], args[1:]
    result = pyeval(expr, *strs)
    sys.displayhook(result)
