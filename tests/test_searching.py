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
    def testGetSearch(self):
        with open('testdata/get_search.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetSearch(term='python')
        self.assertEqual(len(resp), 1)
        self.assertTrue(type(resp[0]), twitter.Status)
        self.assertEqual(resp[0].id, 674342688083283970)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetSearch(since_id='test'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetSearch(max_id='test'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetSearch(term='test', count='test'))
        self.assertFalse(self.api.GetSearch())

    @responses.activate
    def testGetSeachRawQuery(self):
        with open('testdata/get_search_raw.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetSearch(raw_query="q=twitter%20&result_type=recent&since=2014-07-19&count=100")
        self.assertTrue([type(status) is twitter.Status for status in resp])
        self.assertTrue(['twitter' in status.text for status in resp])

    @responses.activate
    def testGetSearchGeocode(self):
        with open('testdata/get_search_geocode.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetSearch(
            term="python",
            geocode=('37.781157', '-122.398720', '100mi'))
        status = resp[0]
        self.assertTrue(status, twitter.Status)
        self.assertTrue(status.geo)
        self.assertEqual(status.geo['type'], 'Point')
        resp = self.api.GetSearch(
            term="python",
            geocode=('37.781157,-122.398720,100mi'))
        status = resp[0]
        self.assertTrue(status, twitter.Status)
        self.assertTrue(status.geo)

    @responses.activate
    def testGetUsersSearch(self):
        with open('testdata/get_users_search.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetUsersSearch(term='python')
        self.assertEqual(type(resp[0]), twitter.User)
        self.assertEqual(len(resp), 20)
        self.assertEqual(resp[0].id, 63873759)
        self.assertRaises(twitter.TwitterError,
                          lambda: self.api.GetUsersSearch(term='python',
                                                          count='test'))
