# encoding: utf-8
from __future__ import unicode_literals, print_function

import json
import re
import sys
import unittest
import warnings

import twitter
import responses
from responses import GET

warnings.filterwarnings('ignore', category=DeprecationWarning)

DEFAULT_URL = re.compile(r'https?://.*\.twitter.com/1\.1/.*')


class ModelsChangesTest(unittest.TestCase):
    """Test how changes to tweets affect model creation"""

    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test',
            sleep_on_rate_limit=False)

    @responses.activate
    def test_extended_in_compat_mode(self):
        """API is in compatibility mode, but we call GetStatus on a tweet that
        was written in extended mode.

        The tweet in question is exactly 140 characters and attaches a photo.

        """
        with open('testdata/3.2/extended_tweet_in_compat_mode.json') as f:
            resp_data = f.read()
        status = twitter.Status.NewFromJsonDict(json.loads(resp_data))
        self.assertTrue(status)
        self.assertEqual(status.id, 782737772490600448)
        self.assertEqual(status.text, "has more details about these changes.  Thanks for making more expressive!writing requirements to python_twitt pytho… https://t.co/et3OTOxWSa")
        self.assertEqual(status.tweet_mode, 'compatibility')
        self.assertTrue(status.truncated)

    @responses.activate
    def test_extended_in_extended_mode(self):
        """API is in extended mode, and we call GetStatus on a tweet that
        was written in extended mode.

        The tweet in question is exactly 140 characters and attaches a photo.

        """
        with open('testdata/3.2/extended_tweet_in_extended_mode.json') as f:
            resp_data = f.read()
        status = twitter.Status.NewFromJsonDict(json.loads(resp_data))
        self.assertTrue(status)
        self.assertEqual(status.id, 782737772490600448)
        self.assertEqual(status.full_text, "has more details about these changes.  Thanks for making more expressive!writing requirements to python_twitt python_twitter.egg-info/SOURCE https://t.co/JWSPztfoyt")
        self.assertEqual(status.tweet_mode, 'extended')
        self.assertFalse(status.truncated)
