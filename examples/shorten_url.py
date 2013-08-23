#!/usr/bin/env python
#
# Copyright 2007-2013 The Python-Twitter Developers
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

'''A class that defines the default URL Shortener.

TinyURL is provided as the default and as an example.
'''

import urllib


 # Change History
 #
 # 2010-05-16
 #     TinyURL example and the idea for this comes from a bug filed by
 #     acolorado with patch provided by ghills.  Class implementation
 #     was done by bear.
 #
 #     Issue 19 http://code.google.com/p/python-twitter/issues/detail?id=19
 #


class ShortenURL(object):
    '''Helper class to make URL Shortener calls if/when required'''
    def __init__(self,
                 userid=None,
                 password=None):
        '''Instantiate a new ShortenURL object
        
        Args:
            userid:   userid for any required authorization call [optional]
            password: password for any required authorization call [optional]
        '''
        self.userid   = userid
        self.password = password

    def Shorten(self,
               longURL):
        '''Call TinyURL API and returned shortened URL result
        
        Args:
            longURL: URL string to shorten
        
        Returns:
            The shortened URL as a string

        Note:
            longURL is required and no checks are made to ensure completeness
        '''

        result = None
        f      = urllib.urlopen("http://tinyurl.com/api-create.php?url=%s" % longURL)
        try:
            result = f.read()
        finally:
            f.close()

        return result
