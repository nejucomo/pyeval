pyeval
======

Evaluate python expressions conveniently from the shell:

.. code-block:: bash

    $ pip install pyeval
    ...

    $ pyeval 'math.cos(math.pi * 2)'
    1.0

Examples
~~~~~~~~

Do you find yourself writing Makefiles, configuration, or build scripts with commands like this?

.. code-block:: bash

    $ PYVER=$(python -c 'import sys; print "%d.%d" % tuple(sys.version_info[:2])')
    $ echo $PYVER
    2.6

Maybe you want to see where a module is loaded from:

.. code-block:: bash

    $ python -c 'import simplejson; print simplejson'
    <module 'simplejson' from '.../virtualenvs/default/lib/python2.7/site-packages/simplejson/__init__.pyc'>

Or perhaps you want to calculate an arithmetic value that's more complex than ``eval`` can handle?

.. code-block:: bash

    $ python -c 'print 2 ** 35'
    34359738368

    $ python -c 'print math.cos(0.1 * math.pi)'
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
    NameError: name 'math' is not defined

Oops! Forgot to import ``math``. Let's try again:

.. code-block:: bash

    $ python -c 'import math; print math.cos(0.1 * math.pi)'
    0.951056516295

Now you can simplify these kinds of tasks with ``pyeval``:

.. code-block:: bash

    $ pip install pyeval
    ...

    $ pyeval 'sh("%d.%d" % tuple(sys.version_info[:2]))'
    2.7

    $ pyeval simplejson
    <AutoImporter proxy for module 'simplejson' from '.../virtualenvs/default/lib/python2.7/site-packages/simplejson/__init__.pyc'>

    $ pyeval '2 ** 35'
    34359738368

    $ pyeval 'math.cos(0.1 * math.pi)'
    0.951056516295

Online Help
~~~~~~~~~~~

To get started, run:

.. code-block:: bash

    $ pyeval help

Upgrading
~~~~~~~~~

If you used ``pyeval 0.1.6``, the output format and ``AutoImporter``
interfaces have changed. To learn how, run:

To get started, run:

.. code-block:: bash

    $ pyeval help upgrading
