#!/usr/bin/env python

import os, sys
from setuptools import setup, find_packages


if 'upload' in sys.argv:
    if '--sign' not in sys.argv and sys.argv[1:] != ['upload', '--help']:
        raise SystemExit('Refusing to upload unsigned packages.')


setup(name='pyeval',
      description='Conveniently evaluate expressions from the shell',
      version='0.2.1a0',
      author='Nathan Wilcox',
      author_email='nejucomo@gmail.com',
      license='GPLv3',
      url='https://bitbucket.org/nejucomo/pyeval',
      scripts=[os.path.join('bin', 'pyeval')],
      packages=find_packages(),
      package_data={'pyeval': ['doc/*.txt']},
      )
