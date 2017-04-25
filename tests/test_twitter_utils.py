# encoding: utf-8

import unittest

import twitter

from twitter.twitter_utils import (
    calc_expected_status_length,
    parse_media_file
)


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test',
            sleep_on_rate_limit=False)
        self.base_url = 'https://api.twitter.com/1.1'

    def test_parse_media_file_http(self):
        data_file, filename, file_size, media_type = parse_media_file(
            'https://raw.githubusercontent.com/bear/python-twitter/master/testdata/168NQ.jpg')
        self.assertTrue(hasattr(data_file, 'read'))
        self.assertEqual(filename, '168NQ.jpg')
        self.assertEqual(file_size, 44772)
        self.assertEqual(media_type, 'image/jpeg')

    def test_parse_media_file_local_file(self):
        data_file, filename, file_size, media_type = parse_media_file(
            'testdata/168NQ.jpg')
        self.assertTrue(hasattr(data_file, 'read'))
        self.assertEqual(filename, '168NQ.jpg')
        self.assertEqual(file_size, 44772)
        self.assertEqual(media_type, 'image/jpeg')

    def test_parse_media_file_fileobj(self):
        with open('testdata/168NQ.jpg', 'rb') as f:
            data_file, filename, file_size, media_type = parse_media_file(f)
            self.assertTrue(hasattr(data_file, 'read'))
            self.assertEqual(filename, '168NQ.jpg')
            self.assertEqual(file_size, 44772)
            self.assertEqual(media_type, 'image/jpeg')

    def test_utils_error_checking(self):
        with open('testdata/168NQ.jpg', 'r') as f:
            self.assertRaises(
                twitter.TwitterError,
                lambda: parse_media_file(f))

        with open('testdata/user_timeline.json', 'rb') as f:
            self.assertRaises(
                twitter.TwitterError,
                lambda: parse_media_file(f))

        self.assertRaises(
            twitter.TwitterError,
            lambda: twitter.twitter_utils.enf_type('test', int, 'hi'))

    def test_calc_expected_status_length(self):
        status = 'hi a tweet there'
        len_status = calc_expected_status_length(status)
        self.assertEqual(len_status, 16)

    def test_calc_expected_status_length_with_url(self):
        status = 'hi a tweet there example.com'
        len_status = calc_expected_status_length(status)
        self.assertEqual(len_status, 40)

    def test_calc_expected_status_length_with_url_and_extra_spaces(self):
        status = 'hi a tweet          there               example.com'
        len_status = calc_expected_status_length(status)
        self.assertEqual(len_status, 63)
