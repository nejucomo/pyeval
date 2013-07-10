#!/usr/bin/env python

import os
from distutils.core import setup

setup(name='pyeval',
      description='Conveniently evaluate expressions from the shell',
      version='0.1.6-dev',
      author='Nathan Wilcox',
      author_email='nejucomo@gmail.com',
      license='GPLv3',
      url='https://bitbucket.org/nejucomo/pyeval/wiki/Home',
      scripts=[os.path.join('bin', 'pyeval')],
      py_modules=[os.path.join('lib', 'pyeval')],
      )
