# encoding: utf-8
from __future__ import unicode_literals, print_function

import json
import re
import sys
import unittest
import warnings

import twitter
from twitter import twitter_utils

import responses
from responses import GET, POST

warnings.filterwarnings('ignore', category=DeprecationWarning)


DEFAULT_URL = re.compile(r'https?://.*\.twitter.com/1\.1/.*')
URLS = {
    "is_url": [
        "t.co/test"
        "http://foo.com/blah_blah",
        "http://foo.com/blah_blah/",
        "http://foo.com/blah_blah_(wikipedia)",
        "http://foo.com/blah_blah_(wikipedia)_(again)",
        "http://www.example.com/wpstyle/?p=364",
        "https://www.example.com/foo/?bar=baz&inga=42&quux",
        # "http://✪df.ws/123",
        # "https://➡.ws/",
        # "http://➡.ws/䨹",
        # "http://⌘.ws",
        # "http://⌘.ws/",
        "http://foo.com/blah_(wikipedia)#cite-1",
        "http://foo.com/blah_(wikipedia)_blah#cite-1",
        "http://foo.com/(something)?after=parens",
        # "http://☺.damowmow.com/",
        "http://code.google.com/events/#&product=browser",
        "http://j.mp",
        "http://foo.bar/?q=Test%20URL-encoded%20stuff",
        "http://1337.net",
        "http://example.com/2.3.1.3/"
        "http://a.b-c.de",
        "foo.com"
    ],
    "is_not_url": [
        "http://userid:password@example.com:8080",
        "http://userid:password@example.com:8080/",
        "http://userid@example.com",
        "http://userid@example.com/",
        "http://userid@example.com:8080",
        "http://userid@example.com:8080/",
        "http://userid:password@example.com",
        "http://userid:password@example.com/",
        "http://142.42.1.1/",
        "2.3",
        ".hello.com",
        "http://142.42.1.1:8080/",
        "ftp://foo.bar/baz",
        "http://مثال.إختبار",
        "http://例子.测试",
        "http://उदाहरण.परीक्षा",
        "http://",
        "http://.",
        "http://..",
        "http://../",
        "http://?",
        "http://??",
        "http://??/",
        "http://#",
        "http://##",
        "http://##/",
        "//",
        "//a",
        "///a",
        "///",
        "http:///a",
        "rdar://1234",
        "h://test",
        ":// should fail",
        "ftps://foo.bar/",
        "http://-error-.invalid/",
        # "http://a.b--c.de/",
        # "http://-a.b.co",
        # "http://a.b-.co",
        "http://223.255.255.254",
        "http://0.0.0.0",
        "http://10.1.1.0",
        "http://10.1.1.255",
        "http://224.1.1.1",
        "http://1.1.1.1.1",
        "http://123.123.123",
        "http://3628126748",
        "http://.www.foo.bar/",
        "http://.www.foo.bar./",
        "http://10.1.1.1"
        "S.84",
        "http://s.84",
        "L.512+MVG",
        "http://L.512+MVG"
    ]
}


class TestUrlRegex(unittest.TestCase):

    def test_yes_urls(self):
        for yes_url in URLS['is_url']:
            self.assertTrue(twitter_utils.is_url(yes_url), yes_url)

    def test_no_urls(self):
        for no_url in URLS['is_not_url']:
            self.assertFalse(twitter_utils.is_url(no_url), no_url)

    def test_regex_finds_unicode(self):
        string = "http://www.➡.ws"
        string2 = "http://www.example.com"
        pattern = re.compile(r'➡', re.U | re.I)
        pattern2 = re.compile(r'(?:http?://|www\\.)*(?:[\w+-_][.])', re.I | re.U)
        self.assertTrue(re.findall(pattern, string))
        self.assertTrue(re.findall(pattern2, string2))
        self.assertTrue(re.findall(pattern2, string))
