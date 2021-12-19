#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

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

import os
import re
import codecs

from setuptools import setup, find_packages


cwd = os.path.abspath(os.path.dirname(__file__))

def read(filename):
    with codecs.open(os.path.join(cwd, filename), 'rb', 'utf-8') as h:
        return h.read()

def convert_txt(txt):
    lst_txt = txt.split('\n')
    for i in range(len(lst_txt)):
        line = lst_txt[i]
        match = re.match(r' +(\S.+)', line)
        if match is not None:
            lst_txt[i] = '\n| {}'.format(match.group(1))
        else:
            match_date = re.match(r'(\d+-\d+-\d+)', line)
            if match_date is not None:
                lst_txt[i] = '\n**{}**'.format(match_date.group(1))
    return '\n'.join(lst_txt)

metadata = read(os.path.join(cwd, 'twitter', '__init__.py'))

def extract_metaitem(meta):
    # swiped from https://hynek.me 's attr package
    meta_match = re.search(r"""^__{meta}__\s+=\s+['\"]([^'\"]*)['\"]""".format(meta=meta),
                           metadata, re.MULTILINE)
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError('Unable to find __{meta}__ string.'.format(meta=meta))

setup(
    name='python-twitter',
    version=extract_metaitem('version'),
    license=extract_metaitem('license'),
    description=extract_metaitem('description'),
    long_description=(read('README.rst') + '\n\n' +
                      read('AUTHORS.rst') + '\n\n' +
                      convert_txt(read('CHANGES'))),
    long_description_content_type = 'text/x-rst',
    author=extract_metaitem('author'),
    author_email=extract_metaitem('email'),
    maintainer=extract_metaitem('author'),
    maintainer_email=extract_metaitem('email'),
    url=extract_metaitem('url'),
    download_url=extract_metaitem('download_url'),
    packages=find_packages(exclude=('tests', 'docs')),
    platforms=['Any'],
    install_requires=['requests', 'requests-oauthlib', 'filetype'],
    tests_require=['pytest'],
    keywords='twitter api',
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
        'Programming Language :: Python :: 3.6',
    ],
)
