# -*- coding: utf-8 -*-

__all__ = ['p', 'pp', 'sh']


import pprint


def pp(_, *a, **kw):
    r"""
    An alias to pprint.pprint.  This is useful when you want to explicitly
    see None, which the default display hook elides:

      $ pyeval '{}.get("monkey")'

      $ pyeval 'pp({}.get("monkey"))'
      None
    """
    pprint.pprint(*a, **kw)


def p(scope, x):
    r"""
    A wrapper around print().  Use this if you want to avoid pretty
    printed results:

      $ pyeval 'p({}.get("nothing"))'
      None

      $ pyeval 'list(range(5))'
      [0, 1, 2, 3, 4]

      $ pyeval 'p(list(range(5)))'
      [0, 1, 2, 3, 4]

    Also, it allows you to print strings directly:

      $ pyeval 'p("x\ty\nz")'
      x	y
      z

    Note, it's possible to display unicode this way:

      $ pyeval 'p(u"\u2606")'
      ☆

    For more details on the encoding, run:

      $ pyeval help encoding
      ...
    """
    print(x)


def sh(scope, obj):
    r"""
    Display the argument in a "shell friendly manner":

    1. If obj is None, display nothing.

    2. If obj is not iterable, treat it as [obj] in the following steps:

    For each item in the iterable:

    3. Convert the item to a string as: str(item)

    4. Print the result with p().

    NOTE: This was the default display behavior of pyeval <=
    2.1.6, so to produce the equivalent output in pyeval > 2.1.6,
    wrap the expression in 'sh(...)'.

    An example of emulating grep

      $ echo -e 'food\nmonkey\nfool' | grep '^foo'
      food
      fool

      $ echo -e 'food\nmonkey\nfool' | pyeval 'sh( l for l in ilines if l.startswith("foo") )'
      food
      fool
    """
    p = scope['p']

    if obj is None:
        return

    it = [obj]
    if not isinstance(obj, str):
        try:
            it = iter(obj)
        except TypeError:
            pass

    for elem in it:
        p(str(elem))
