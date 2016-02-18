#!/usr/bin/env python

# Copyright 2007-2016 The Python-Twitter Developers

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ----------------------------------------------------------------------
# Change History
#
# 2010-05-16
#   TinyURL example and the idea for this comes from a bug filed by
#   acolorado with patch provided by ghills.  Class implementation
#   was done by @bear.
#
#   Issue #19: http://code.google.com/p/python-twitter/issues/detail?id=19
#
# 2016-02-18
#   Updated example with code to demonstrate passing a status message through
#   a shortener and then off to PostUpdate. Implemenation by @jeremylow from
#   bug filed by @immanuelfactor
#
#   Issue #298: https://github.com/bear/python-twitter/issues/298

# ----------------------------------------------------------------------
# This file demonstrates how to shorten all URLs contained within a Tweet
# by passing the tweet text to a shortener. In this case, we're using TinyURL
# since it does not require any real authentication for our purposes. If you
# are using a different service to shorten URLs, then you will need to modify
# the ShortenURL class to suit your needs.

# Note that this example shortens all URLs contained within the Tweet text.

# To use this example, replace the W/X/Y/Zs with your keys obtained from
# Twitter, or uncomment the lines for getting an environment variable. If you
# are using a virtualenv on Linux, you can set environment variables in the
# ~/VIRTUALENVDIR/bin/activate script.

# If you need assistance with obtaining keys from Twitter, see the instructions
# in doc/getting_started.rst.


import re
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

from twitter import Api
from twitter.twitter_utils import URL_REGEXP


class ShortenURL(object):
    """ A class that defines the default URL Shortener.

    TinyURL is provided as the default and as an example helper class to make
    URL Shortener calls if/when required. """

    def __init__(self,
                 userid=None,
                 password=None):
        """Instantiate a new ShortenURL object. TinyURL, which is used for this
        example, does not require a userid or password, so you can try this
        out without specifying either.

        Args:
            userid:   userid for any required authorization call [optional]
            password: password for any required authorization call [optional]
        """
        self.userid = userid
        self.password = password

    def Shorten(self,
                long_url):
        """ Call TinyURL API and returned shortened URL result.

        Args:
            long_url: URL string to shorten

        Returns:
            The shortened URL as a string

        Note:
            long_url is required and no checks are made to ensure completeness
        """

        result = None
        f = urlopen("http://tinyurl.com/api-create.php?url={0}".format(
            long_url))
        try:
            result = f.read()
        finally:
            f.close()

        # The following check is required for py2/py3 compatibility, since
        # urlopen on py3 returns a bytes-object, and urlopen on py2 returns a
        # string.
        if isinstance(result, bytes):
            return result.decode('utf8')
        else:
            return result


def _get_api():
    # Either specify a set of keys here or use os.getenv('CONSUMER_KEY') style
    # assignment:

    CONSUMER_KEY = 'WWWWWWWW'
    # CONSUMER_KEY = os.getenv("CONSUMER_KEY", None)
    CONSUMER_SECRET = 'XXXXXXXX'
    # CONSUMER_SECRET = os.getenv("CONSUMER_SECRET", None)
    ACCESS_TOKEN = 'YYYYYYYY'
    # ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)
    ACCESS_TOKEN_SECRET = 'ZZZZZZZZ'
    # ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", None)

    return Api(CONSUMER_KEY,
               CONSUMER_SECRET,
               ACCESS_TOKEN,
               ACCESS_TOKEN_SECRET)


def PostStatusWithShortenedURL(status):
    shortener = ShortenURL()
    api = _get_api()

    # Find all URLs contained within the status message. Value of ``urls`` will
    # be a list.
    urls = re.findall(URL_REGEXP, status)

    for url in urls:
        status = status.replace(url, shortener.Shorten(url), 1)

    api.PostUpdate(status)


if __name__ == '__main__':
    PostStatusWithShortenedURL("this is a test: http://www.example.com/tests")
