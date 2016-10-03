# encoding: utf-8
from __future__ import unicode_literals, print_function

import json
import re
import sys
import unittest
import warnings

import twitter
import responses
from responses import GET, POST

warnings.filterwarnings('ignore', category=DeprecationWarning)

DEFAULT_URL = re.compile(r'https?://.*\.twitter.com/1\.1/.*')
BODY = b'{"request":"\\/1.1\\/statuses\\/user_timeline.json","error":"Not authorized."}'


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test',
            sleep_on_rate_limit=False,
            chunk_size=500 * 1024)

    @responses.activate
    def testGetShortUrlLength(self):
        responses.add(GET, DEFAULT_URL, body=BODY, status=401)

        try:
            resp = self.api.GetUserTimeline(screen_name="twitter")
        except twitter.TwitterError as e:
            self.assertEqual(e.message, "Not authorized.")
