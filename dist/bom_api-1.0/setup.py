#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 09:10:02 2018

@author: brendan
"""

from setuptools import setup, find_packages

setup(name = "bom_api",
      version = "1.0",
      description = "An API to query and modify a bill of materials",
      author = 'Brendan Folie',
      author_email = "bfolie@berkeley.edu",
      packages = find_packages(),
      include_package_data=True,
      install_requires = ['flask'],
      setup_requires=['pytest-runner'],
      tests_require = ['pytest']
)