#!/usr/bin/env python
#
# vim: sw=2 ts=2 sts=2
#
# Copyright 2007 The Python-Twitter Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A library that provides a Python interface to the Twitter API"""
from __future__ import absolute_import

__author__ = 'python-twitter@googlegroups.com'
__version__ = '2.3'

import json                                 # noqa

try:
    from hashlib import md5                 # noqa
except ImportError:
    from md5 import md5                     # noqa

from ._file_cache import _FileCache         # noqa
from .error import TwitterError             # noqa
from .direct_message import DirectMessage   # noqa
from .hashtag import Hashtag                # noqa
from .parse_tweet import ParseTweet         # noqa
from .trend import Trend                    # noqa
from .url import Url                        # noqa
from .status import Status                  # noqa
from .user import User, UserStatus          # noqa
from .category import Category              # noqa
from .media import Media                    # noqa
from .list import List                      # noqa
from .api import Api                        # noqa
