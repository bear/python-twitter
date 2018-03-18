# encoding: utf-8
from __future__ import unicode_literals

import sys
import unittest

import responses

import twitter
from twitter.twitter_utils import (
    calc_expected_status_length,
    parse_media_file
)

from twitter import twitter_utils as utils

if sys.version_info > (3,):
    unicode = str


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test',
            sleep_on_rate_limit=False)
        self.base_url = 'https://api.twitter.com/1.1'

    @responses.activate
    def test_parse_media_file_http(self):
        with open('testdata/168NQ.jpg', 'rb') as f:
            img_data = f.read()
        responses.add(
            responses.GET,
            url='https://raw.githubusercontent.com/bear/python-twitter/master/testdata/168NQ.jpg',
            body=img_data)
        data_file, filename, file_size, media_type = parse_media_file(
            'https://raw.githubusercontent.com/bear/python-twitter/master/testdata/168NQ.jpg')
        self.assertTrue(hasattr(data_file, 'read'))
        self.assertEqual(filename, '168NQ.jpg')
        self.assertEqual(file_size, 44772)
        self.assertEqual(media_type, 'image/jpeg')

    @responses.activate
    def test_parse_media_file_http_with_query_strings(self):
        with open('testdata/168NQ.jpg', 'rb') as f:
            img_data = f.read()
        responses.add(
            responses.GET,
            url='https://raw.githubusercontent.com/bear/python-twitter/master/testdata/168NQ.jpg',
            body=img_data)
        data_file, filename, file_size, media_type = parse_media_file(
            'https://raw.githubusercontent.com/bear/python-twitter/master/testdata/168NQ.jpg?query=true')
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

    def test_calc_expected_status_length_with_wide_unicode(self):
        status = "…"
        len_status = calc_expected_status_length(status)
        assert len_status == 2
        status = "……"
        len_status = calc_expected_status_length(status)
        assert len_status == 4

    def test_parse_args(self):
        user = twitter.User(screen_name='__jcbl__')
        out = utils.parse_arg_list(user, 'screen_name')
        assert isinstance(out, (str, unicode))
        assert out == '__jcbl__'

        users = ['__jcbl__', 'notinourselves']
        out = utils.parse_arg_list(users, 'screen_name')
        assert isinstance(out, (str, unicode))
        assert out == '__jcbl__,notinourselves'

        users2 = [user] + users
        out = utils.parse_arg_list(users2, 'screen_name')
        assert isinstance(out, (str, unicode))
        assert out == '__jcbl__,__jcbl__,notinourselves'

        users = '__jcbl__'
        out = utils.parse_arg_list(users, 'screen_name')
        assert isinstance(out, (str, unicode))
        assert out == '__jcbl__'
