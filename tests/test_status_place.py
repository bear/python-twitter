import unittest
import re
import sys
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


class ApiPlaceTest(unittest.TestCase):
    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test'
        )
        self.base_url = 'https://api.twitter.com/1.1'
        self._stderr = sys.stderr
        sys.stderr = ErrNull()

    def tearDown(self):
        sys.stderr = self._stderr
        pass

    @responses.activate
    def testGetStatusWithPlace(self):
        with open('testdata/get_status_with_place.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetStatus(1051204790334746624)
        self.assertTrue(isinstance(resp, twitter.Status))
        self.assertTrue(isinstance(resp.place, twitter.Place))
        self.assertEqual(resp.id, 1051204790334746624)

    @responses.activate
    def testPostUpdateWithPlace(self):
        with open('testdata/post_update_with_place.json') as f:
            resp_data = f.read()
        responses.add(POST, DEFAULT_URL, body=resp_data, status=200)

        post = self.api.PostUpdate('test place', place_id='07d9db48bc083000')
        self.assertEqual(post.place.id, '07d9db48bc083000')
