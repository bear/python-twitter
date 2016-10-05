# encoding: utf-8

import json
import pickle
import re
import sys
import unittest
import warnings

import responses
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

    def test_trend_repr1(self):
        trend = twitter.Trend(
            name="#نفسك_تبيع_ايه_للسعوديه",
            url="http://twitter.com/search?q=%23ChangeAConsonantSpoilAMovie",
            timestamp='whatever')
        try:
            trend.__repr__()
        except Exception as e:
            self.fail(e)

    def test_trend_repr2(self):
        trend = twitter.Trend(
            name="#N\u00e3oD\u00eaUnfTagueirosSdv",
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
            print(r.__str__())
            try:
                r.__repr__()
            except Exception as e:
                self.fail(e)

    @responses.activate
    def test_unicode_get_search(self):
        responses.add(responses.GET, DEFAULT_URL, body=b'{}', status=200)
        try:
            self.api.GetSearch(term="#ابشري_قابوس_جاء")
        except Exception as e:
            self.fail(e)

    def test_constructed_status(self):
        s = twitter.Status()
        s.text = "可以倒着飞的飞机"
        s.created_at = "016-02-13T23:00:00"
        s.screen_name = "himawari8bot"
        s.id = 1
        try:
            s.__repr__()
        except Exception as e:
            self.fail(e)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ApiTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
