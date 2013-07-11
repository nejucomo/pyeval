__all__ = ['main']

import sys

from pyeval.eval import pyevalAndDisplay


def main(args = sys.argv[1:]):
    pyevalAndDisplay(*args)

