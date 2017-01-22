# encoding: utf-8
from __future__ import unicode_literals, print_function

import json
import re
import sys
import unittest

import twitter

import responses
from responses import GET, POST

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

    @responses.activate
    def testGetCollectionEntries(self):
        with open('testdata/collections/get_collections_entries.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            DEFAULT_URL,
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetCollectionEntries('custom-611975872132689921')

        self.assertTrue(resp)
        self.assertEqual(resp.id, 'custom-611975872132689921')
        self.assertEqual(len(resp.statuses), 12)
        self.assertEqual(resp.statuses[0].id, 609497036921044993)
        self.assertTrue(resp.timeline)

    @responses.activate
    def testGetCollection(self):
        with open('testdata/collections/get_collections_show.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data, status=200)
        resp = self.api.GetCollection(collection_id='custom-611975872132689921')

        self.assertTrue(resp)
        self.assertEqual(resp.id, 'custom-611975872132689921')
        self.assertEqual(resp.user.screen_name, 'TwitterMusic')

    @responses.activate
    def testGetCollectionList(self):
        with open('testdata/collections/get_collections_list.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data, status=200)
        resp = self.api.GetCollectionList(screen_name='TwitterMusic')

        self.assertTrue(resp)
        self.assertEqual(len(resp[2]), 20)
        self.assertTrue([isinstance(coll, twitter.Collection) for coll in resp[2]])
        self.assertEqual(resp[2][0].user.screen_name, 'TwitterMusic')
