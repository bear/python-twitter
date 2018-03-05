# encoding: utf-8

import json
import pickle
import re
import sys
import unittest
import warnings

import responses

from hypothesis import given, example
from hypothesis import strategies as st

import twitter

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
        self.maxDiff = None
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

    @given(text=st.text())
    @example(text="#نفسك_تبيع_ايه_للسعوديه")
    def test_trend_repr1(self, text):
        trend = twitter.Trend(
            name=text,
            url="http://twitter.com/search?q=%23ChangeAConsonantSpoilAMovie",
            timestamp='whatever')
        try:
            trend.__repr__()
        except Exception as e:
            self.fail(e)

    @given(text=st.text())
    @example(text="#N\u00e3oD\u00eaUnfTagueirosSdv")
    def test_trend_repr2(self, text):
        trend = twitter.Trend(
            url='http://twitter.com/search?q=%23ChangeAConsonantSpoilAMovie',
            timestamp='whatever')

        try:
            trend.__repr__()
        except Exception as e:
            self.fail(e)

    @responses.activate
    def test_trend_repr3(self):
        with open('testdata/get_trends_current_unicode.json', 'r') as f:
            resp_data = f.read()

        responses.add(
            responses.GET, DEFAULT_URL, body=resp_data, match_querystring=True)

        resp = self.api.GetTrendsCurrent()
        for r in resp:
            try:
                r.__repr__()
            except Exception as e:
                self.fail(e)

    @given(text=st.text())
    @responses.activate
    def test_unicode_get_search(self, text):
        responses.add(responses.GET, DEFAULT_URL, body=b'{}', status=200)
        try:
            self.api.GetSearch(term=text)
        except Exception as e:
            self.fail(e)

    @given(text=st.text())
    @example(text='可以倒着飞的飞机')
    def test_constructed_status(self, text):
        s = twitter.Status()
        s.text = text
        s.created_at = "016-02-13T23:00:00"
        s.screen_name = "himawari8bot"
        s.id = 1
        try:
            s.__repr__()
        except Exception as e:
            self.fail(e)

    def test_post_with_bytes_string(self):
        status = 'x'
        length = twitter.twitter_utils.calc_expected_status_length(status)
        assert length == 1
