# encoding: utf-8

import json
import sys
import unittest

import twitter
import responses


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
            sleep_on_rate_limit=False)
        self.base_url = 'https://api.twitter.com/1.1'
        self._stderr = sys.stderr
        sys.stderr = ErrNull()

    def tearDown(self):
        sys.stderr = self._stderr
        pass

    @responses.activate
    def testGetFriendIDs(self):
        # First request for first 5000 friends
        with open('testdata/get_friend_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/ids.json?screen_name=EricHolthaus&count=5000&stringify_ids=False&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining friends
        with open('testdata/get_friend_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/ids.json?count=5000&screen_name=EricHolthaus&stringify_ids=False&cursor=1417903878302254556'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        resp = self.api.GetFriendIDs(screen_name='EricHolthaus')
        self.assertTrue(type(resp) is list)
        self.assertEqual(len(resp), 6452)
        self.assertTrue(type(resp[0]) is int)

        # Error checking
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFriendIDs(total_count='infinity'))

    @responses.activate
    def testGetFriendIDsPaged(self):
        with open('testdata/get_friend_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/ids.json?count=5000&cursor=-1&screen_name=EricHolthaus&stringify_ids=False'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFriendIDsPaged(screen_name='EricHolthaus')
        self.assertLessEqual(len(resp), 5000)
        self.assertTrue(ncursor)
        self.assertFalse(pcursor)

    @responses.activate
    def testGetFriendsPaged(self):
        with open('testdata/get_friends_paged.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/list.json?screen_name=codebear&count=200&cursor=-1&skip_status=False&include_user_entities=True'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFriendsPaged(screen_name='codebear', count=200)
        self.assertEqual(ncursor, 1494734862149901956)
        self.assertEqual(pcursor, 0)
        self.assertEqual(len(resp), 200)
        self.assertTrue(type(resp[0]) is twitter.User)

        with open('testdata/get_friends_paged_uid.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/list.json?user_id=12&skip_status=False&cursor=-1&include_user_entities=True&count=200'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFriendsPaged(user_id=12, count=200)
        self.assertEqual(ncursor, 1510410423140902959)
        self.assertEqual(pcursor, 0)
        self.assertEqual(len(resp), 200)
        self.assertTrue(type(resp[0]) is twitter.User)

        with open('testdata/get_friends_paged_additional_params.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/list.json?include_user_entities=True&user_id=12&count=200&cursor=-1&skip_status=True'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFriendsPaged(user_id=12,
                                                          count=200,
                                                          skip_status=True,
                                                          include_user_entities=True)
        self.assertEqual(ncursor, 1510492845088954664)
        self.assertEqual(pcursor, 0)
        self.assertEqual(len(resp), 200)
        self.assertTrue(type(resp[0]) is twitter.User)

    @responses.activate
    def testGetFriends(self):

        """
        This is tedious, but the point is to add a responses endpoint for
        each call that GetFriends() is going to make against the API and
        have it return the appropriate json data.
        """

        cursor = -1
        for i in range(0, 5):
            with open('testdata/get_friends_{0}.json'.format(i)) as f:
                resp_data = f.read()
            endpoint = '/friends/list.json?screen_name=codebear&count=200&skip_status=False&include_user_entities=True&cursor={0}'.format(cursor)

            responses.add(
                responses.GET,
                '{base_url}{endpoint}'.format(
                    base_url=self.api.base_url,
                    endpoint=endpoint),
                body=resp_data, match_querystring=True, status=200)

            cursor = json.loads(resp_data)['next_cursor']

        resp = self.api.GetFriends(screen_name='codebear')
        self.assertEqual(len(resp), 819)

    @responses.activate
    def testGetFriendsWithLimit(self):
        with open('testdata/get_friends_0.json') as f:
            resp_data = f.read()

        responses.add(
            responses.GET,
            '{base_url}/friends/list.json?include_user_entities=True&skip_status=False&screen_name=codebear&count=200&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        resp = self.api.GetFriends(screen_name='codebear', total_count=200)
        self.assertEqual(len(resp), 200)

    def testFriendsErrorChecking(self):
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFriends(screen_name='jack',
                                        total_count='infinity'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFriendsPaged(screen_name='jack',
                                             count='infinity'))

    @responses.activate
    def testGetFollowersIDs(self):
        # First request for first 5000 followers
        with open('testdata/get_follower_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/ids.json?count=5000&cursor=-1&screen_name=GirlsMakeGames'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining followers
        with open('testdata/get_follower_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/ids.json?cursor=1482201362283529597&count=5000&screen_name=GirlsMakeGames'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        resp = self.api.GetFollowerIDs(screen_name='GirlsMakeGames')
        self.assertTrue(type(resp) is list)
        self.assertEqual(len(resp), 7885)
        self.assertTrue(type(resp[0]) is int)

        # Error checking
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFollowerIDs(count='infinity'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFollowerIDs(total_count='infinity'))

    @responses.activate
    def testGetFollowers(self):
        # First request for first 200 followers
        with open('testdata/get_followers_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/list.json?include_user_entities=True&count=200&screen_name=himawari8bot&skip_status=False&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining followers
        with open('testdata/get_followers_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/list.json?include_user_entities=True&skip_status=False&count=200&screen_name=himawari8bot&cursor=1516850034842747602'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetFollowers(screen_name='himawari8bot')
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(len(resp), 335)

    @responses.activate
    def testGetFollowersPaged(self):
        with open('testdata/get_followers_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/list.json?include_user_entities=True&count=200&screen_name=himawari8bot&skip_status=False&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFollowersPaged(screen_name='himawari8bot')

        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(len(resp), 200)

    @responses.activate
    def testGetFollowerIDsPaged(self):
        with open('testdata/get_follower_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/ids.json?count=5000&stringify_ids=False&screen_name=himawari8bot&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFollowerIDsPaged(
            screen_name='himawari8bot')

        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is int)
        self.assertEqual(len(resp), 5000)

        with open('testdata/get_follower_ids_stringify.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/ids.json?count=5000&stringify_ids=True&user_id=12&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFollowerIDsPaged(
            user_id=12,
            stringify_ids=True)

        self.assertTrue(type(resp) is list)
        if sys.version_info.major >= 3:
            self.assertTrue(type(resp[0]) is str)
        else:
            self.assertTrue(type(resp[0]) is unicode)
        self.assertEqual(len(resp), 5000)
