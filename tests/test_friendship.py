# encoding: utf-8
from __future__ import unicode_literals, print_function

import json
import os
import re
import sys
from tempfile import NamedTemporaryFile
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import warnings

import twitter

import responses
from responses import GET, POST

warnings.filterwarnings('ignore', category=DeprecationWarning)


DEFAULT_URL = re.compile(r'https?://.*\.twitter.com/1\.1/.*')


class ErrNull(object):
    """ Suppress output of tests while writing to stdout or stderr. This just
    takes in data and does nothing with it.
    """

    def write(self, data):
        pass


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test',
            sleep_on_rate_limit=False,
            chunk_size=500 * 1024)
        self.base_url = 'https://api.twitter.com/1.1'
        self._stderr = sys.stderr
        sys.stderr = ErrNull()

    def tearDown(self):
        sys.stderr = self._stderr
        pass

    @responses.activate
    def testCreateFriendship(self):
        with open('testdata/create_friendship.json') as f:
            resp_data = f.read()
        responses.add(POST, DEFAULT_URL, body=resp_data)

        resp = self.api.CreateFriendship(screen_name='facebook')
        self.assertTrue(type(resp), twitter.User)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.CreateFriendship(user_id=None, screen_name=None))

    @responses.activate
    def testUpdateFriendship(self):
        with open('testdata/update_friendship.json') as f:
            resp_data = f.read()
        responses.add(POST, DEFAULT_URL, body=resp_data)

        resp = self.api.UpdateFriendship(user_id=2425151, retweets=False)
        self.assertTrue(type(resp), twitter.User)

    @responses.activate
    def testDestroyFriendship(self):
        with open('testdata/destroy_friendship.json') as f:
            resp_data = f.read()
        responses.add(POST, DEFAULT_URL, body=resp_data)

        resp = self.api.DestroyFriendship(user_id=2425151)
        self.assertTrue(type(resp), twitter.User)

        resp = self.api.DestroyFriendship(screen_name='facebook')
        self.assertTrue(type(resp), twitter.User)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.DestroyFriendship(user_id=None, screen_name=None))
