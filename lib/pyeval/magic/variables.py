__all__ = [
    'encoding',
    'help',
    'i',
    'ilines',
    'lines',
    'ri',
    'rlines',
    'scope',
    ]


import sys
from pyeval.help import HelpBrowser
from pyeval.display import getEncoding


def scope(scope):
    r"""The evaluation scope, an instance of MagicScope."""
    return scope


def encoding(scope):
    r"""The detected encoding used by p() and other magic functions."""
    return getEncoding()


def help(scope):
    r"""The help browser."""
    return HelpBrowser(scope)


def ri(_):
    r"""
      The raw standard input as a string.  The first access calls
      'sys.stdin.read()', so compare these:

        $ echo 'foo' | pyeval 'len(sys.stdin.read())'
        4

        $ echo 'foo' | pyeval 'len(ri)'
        4

      Notice because of magic variable caching, using 'ri' multiple times
      always results in the same input:

        $ echo 'foo' | pyeval '[len(ri), ri.replace("o", "-")]'
        [4, 'f--\n']
    """
    return sys.stdin.read()


def i(scope):
    r"""
    The stripped standard input string.  Defined as 'ri.strip()' so:

      $ echo 'foo' | pyeval 'len(ri.strip())'
      3

      $ echo 'foo' | pyeval 'len(i)'
      3
    """
    return scope['ri'].strip()


def rlines(scope):
    r"""
    The list of raw standard input lines.  Defined as 'ri.split("\\n")'.
    """
    return scope['ri'].split('\n')


def lines(scope):
    r"""
    The list of stripped standard input lines.  Defined as:
    '[ l.strip() for l in scope['rlines'] ]'
    """
    return [ l.strip() for l in scope['rlines'] ]


def ilines(_):
    r"""
    A line iterator over stripped lines from stdin.  Defined as:
    '( l.strip() for l in sys.stdin )'
    """
    return ( l.strip() for l in sys.stdin )
