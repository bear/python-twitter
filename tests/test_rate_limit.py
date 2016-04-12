# encoding: utf-8

import re
import sys
import unittest
import warnings

import twitter
import responses

warnings.filterwarnings('ignore', category=DeprecationWarning)
DEF_URL_RE = re.compile(r'https?://.*\.twitter.com/1\.1/.*')


class ErrNull(object):
    """ Suppress output of tests while writing to stdout or stderr. This just
    takes in data and does nothing with it.
    """

    def write(self, data):
        pass


class RateLimitTests(unittest.TestCase):
    """ Tests for RateLimit object """

    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test',
            sleep_on_rate_limit=False)
        self.base_url = 'https://api.twitter.com/1.1'
        self._stderr = sys.stderr
        sys.stderr = ErrNull()

    def tearDown(self):
        sys.stderr = self._stderr
        pass

    @responses.activate
    def testInitializeRateLimit(self):
        with open('testdata/ratelimit.json') as f:
            resp_data = f.read()

        url = '%s/application/rate_limit_status.json' % self.api.base_url
        responses.add(
            responses.GET,
            url,
            body=resp_data,
            match_querystring=True,
            status=200)
        self.api.InitializeRateLimit()
        self.assertTrue(self.api.rate_limit)

        self.rate_limit = None
        self.api.sleep_on_rate_limit = True
        self.api.InitializeRateLimit()
        self.assertTrue(self.api.rate_limit)
        self.assertTrue(self.api.sleep_on_rate_limit)

        responses.add(responses.GET, url=DEF_URL_RE, body=b'{}', status=200)
        try:
            self.api.GetStatus(status_id=1234)
            self.api.GetUser(screen_name='test')
        except Exception as e:
            self.fail(e)

    @responses.activate
    def testCheckRateLimit(self):
        with open('testdata/ratelimit.json') as f:
            resp_data = f.read()
        url = '%s/application/rate_limit_status.json' % self.api.base_url
        responses.add(
            responses.GET,
            url,
            body=resp_data,
            match_querystring=True,
            status=200)
        rt = self.api.CheckRateLimit('https://api.twitter.com/1.1/help/privacy.json')
        self.assertEqual(rt.limit, 15)
        self.assertEqual(rt.remaining, 15)
        self.assertEqual(rt.reset, 1452254278)


class RateLimitMethodsTests(unittest.TestCase):
    """ Tests for RateLimit object """

    @responses.activate
    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test',
            sleep_on_rate_limit=False)
        self.base_url = 'https://api.twitter.com/1.1'
        self._stderr = sys.stderr
        sys.stderr = ErrNull()

        with open('testdata/ratelimit.json') as f:
            resp_data = f.read()

        url = '%s/application/rate_limit_status.json' % self.api.base_url
        responses.add(
            responses.GET,
            url,
            body=resp_data,
            match_querystring=True,
            status=200)
        self.api.InitializeRateLimit()
        self.assertTrue(self.api.rate_limit)


    def tearDown(self):
        sys.stderr = self._stderr
        pass

    def testGetRateLimit(self):
        lim = self.api.rate_limit.get_limit('/lists/members')
        self.assertEqual(lim.limit, 180)
        self.assertEqual(lim.remaining, 180)
        self.assertEqual(lim.reset, 1452254278)

    def testNonStandardEndpointRateLimit(self):
        lim = self.api.rate_limit.get_limit('https://api.twitter.com/1.1/geo/id/312.json?skip_status=True')
        self.assertEqual(lim.limit, 47)

        lim = self.api.rate_limit.get_limit('https://api.twitter.com/1.1/saved_searches/destroy/312.json')
        self.assertEqual(lim.limit, 15)
        lim = self.api.rate_limit.get_limit('https://api.twitter.com/1.1/statuses/retweets/312.json?skip_status=True')
        self.assertEqual(lim.limit, 23)

    def testSetRateLimit(self):
        previous_limit = self.api.rate_limit.get_limit('/lists/members')
        self.api.rate_limit.set_limit(
            url='https://api.twitter.com/1.1/lists/members.json?skip_status=True',
            limit=previous_limit.limit,
            remaining=previous_limit.remaining - 1,
            reset=previous_limit.reset)
        new_limit = self.api.rate_limit.get_limit('/lists/members')
        self.assertEqual(new_limit.remaining, previous_limit.remaining - 1)

    def testFamilyNotFound(self):
        limit = self.api.rate_limit.get_limit('/tests/test')
        self.assertEqual(limit.limit, 15)
        self.assertEqual(limit.remaining, 15)
        self.assertEqual(limit.reset, 0)

    def testSetUnknownRateLimit(self):
        self.api.rate_limit.set_limit(
            url='https://api.twitter.com/1.1/not/a/real/endpoint.json',
            limit=15,
            remaining=14,
            reset=100)
        limit = self.api.rate_limit.get_limit(
            url='https://api.twitter.com/1.1/not/a/real/endpoint.json')
        self.assertEqual(limit.remaining, 14)
