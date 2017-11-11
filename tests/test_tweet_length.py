# encoding: utf-8

import unittest
import twitter


class TestTweetLength(unittest.TestCase):

    def setUp(self):
        self.api = twitter.Api(consumer_key='test',
                               consumer_secret='test',
                               access_token_key='test',
                               access_token_secret='test')
        self.api._config = {'short_url_length_https': 23}

    def test_find_urls(self):
        url = "http://example.com"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "https://example.com/path/to/resource?search=foo&lang=en"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "http://twitter.com/#!/twitter"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "HTTPS://www.ExaMPLE.COM/index.html"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        # url = "http://user:PASSW0RD@example.com:8080/login.php"
        # self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "http://sports.yahoo.com/nfl/news;_ylt=Aom0;ylu=XyZ?slug=ap-superbowlnotebook"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        # url = "http://192.168.0.1/index.html?src=asdf"
        # self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))

        # Have to figure out what a valid IPv6 range looks like, then
        # uncomment this.
        # url = "http://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html"
        # self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))

        url = "http://test_underscore.twitter.com"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "http://example.com?foo=$bar.;baz?BAZ&c=d-#top/?stories+"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "https://www.youtube.com/playlist?list=PL0ZPu8XSRTB7wZzn0mLHMvyzVFeRxbWn-"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "example.com"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "www.example.com"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "foo.co.jp foo.co.jp foo.co.jp"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "example.com/path/to/resource?search=foo&lang=en"
        self.assertTrue(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "hello index.html my friend"
        self.assertFalse(twitter.twitter_utils.is_url(url), "'{0}'".format(url))
        url = "run.on.sentence"
        self.assertFalse(twitter.twitter_utils.is_url(url), "'{0}'".format(url))

    def test_split_tweets(self):
        test_tweet = (
            "Anatole went out of the room and returned a few minutes later "
            "wearing a fur coat girt with a silver belt, and a sable cap "
            "jauntily set on one side and very becoming to his handsome face. "
            "Having looked in a mirror, and standing before Dolokhov in the "
            "same pose he had assumed before it, he lifted a glass of wine.")
        tweets = self.api._TweetTextWrap(test_tweet)
        self.assertEqual(
            tweets[0],
            "Anatole went out of the room and returned a few minutes later wearing a fur coat girt with a silver belt, and a sable cap jauntily set on one side and very becoming to his handsome face. Having looked in a mirror, and standing before Dolokhov in the same pose he had assumed")
        self.assertEqual(
            tweets[1],
            "before it, he lifted a glass of wine.")

        test_tweet = "t.co went t.co of t.co room t.co returned t.co few minutes later and then t.co went to t.co restroom and t.co was sad because t.co did not have any t.co toilet paper"
        tweets = self.api._TweetTextWrap(test_tweet)
        self.assertEqual(tweets[0], 't.co went t.co of t.co room t.co returned t.co few minutes later and then t.co went to t.co restroom and t.co was sad because')
        self.assertEqual(tweets[1], 't.co did not have any t.co toilet paper')
