#!/usr/bin/env python
from setuptools import find_packages, setup


setup(name='connect_four',
      description='Kendrick\'s connect four assignment',
      author='Kendrick Tang',
      author_email='tangkend@uw.edu',
      url='https://github.com/rafastealth/dataengineer-hw',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=[
          'pymysql',
          'sqlalchemy>1.2',
          'redis',
          'requests',
          ],
      zip_safe=True,
      )
