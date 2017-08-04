__all__ = ['main']

import sys

from pyeval.eval import pyevalAndDisplay


def main(args = sys.argv[1:]):

    if len(args) == 0 or args[0] in ['-h', '--help']:
        args = ['help']

    pyevalAndDisplay(*args)

