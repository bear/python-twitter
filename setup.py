#!/usr/bin/env python
#
# Copyright 2007-2016 The Python-Twitter Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''The setup and build script for the python-twitter library.'''

import os, io

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with io.open(os.path.join(*paths), 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='python-twitter',
    version='3.0rc1',
    author='The Python-Twitter Developers',
    author_email='python-twitter@googlegroups.com',
    license='Apache License 2.0',
    url='https://github.com/bear/python-twitter',
    keywords='twitter api',
    description='A Python wrapper around the Twitter API',
    long_description=(read('README.rst') + '\n\n' +
                      read('AUTHORS.rst') + '\n\n' +
                      read('CHANGES')),
    packages=find_packages(exclude=['tests*']),
    install_requires=['future', 'requests', 'requests-oauthlib'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
