#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name='pyeval',
      description='Conveniently evaluate expressions from the shell',
      version='0.2a1',
      author='Nathan Wilcox',
      author_email='nejucomo@gmail.com',
      license='GPLv3',
      url='https://bitbucket.org/nejucomo/pyeval',

      scripts=[os.path.join('bin', 'pyeval')],
      packages=find_packages('lib'),
      package_dir={'': 'lib'},
      package_data={'pyeval': ['doc/*.txt']},
      )
