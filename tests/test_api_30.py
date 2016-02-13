# encoding: utf-8

import json
import sys
import unittest

import twitter

import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

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

    def testApiSetUp(self):
        self.assertRaises(
            twitter.TwitterError,
            lambda: twitter.Api(consumer_key='test'))

    def testSetAndClearCredentials(self):
        api = twitter.Api()
        api.SetCredentials(consumer_key='test',
                           consumer_secret='test',
                           access_token_key='test',
                           access_token_secret='test')
        self.assertEqual(api._consumer_key, 'test')
        self.assertEqual(api._consumer_secret, 'test')
        self.assertEqual(api._access_token_key, 'test')
        self.assertEqual(api._access_token_secret, 'test')

        api.ClearCredentials()

        self.assertFalse(all([
            api._consumer_key,
            api._consumer_secret,
            api._access_token_key,
            api._access_token_secret
        ]))

    @responses.activate
    def testApiRaisesAuthErrors(self):
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/search/tweets.json?count=15&result_type=mixed&q=python',
            body='',
            match_querystring=True,
            status=200)
        api = twitter.Api()
        api.SetCredentials(consumer_key='test',
                           consumer_secret='test',
                           access_token_key='test',
                           access_token_secret='test')
        api._Api__auth = None
        self.assertRaises(twitter.TwitterError, lambda: api.GetFollowers())

    @responses.activate
    def testGetHelpConfiguration(self):
        with open('testdata/get_help_configuration.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/help/configuration.json',
            body=resp_data,
            status=200)
        resp = self.api.GetHelpConfiguration()
        self.assertEqual(resp.get('short_url_length_https'), 23)

    @responses.activate
    def testGetShortUrlLength(self):
        with open('testdata/get_help_configuration.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/help/configuration.json',
            body=resp_data,
            status=200)
        resp = self.api.GetShortUrlLength()
        self.assertEqual(resp, 23)
        resp = self.api.GetShortUrlLength(https=True)
        self.assertEqual(resp, 23)

    @responses.activate
    def testGetSearch(self):
        with open('testdata/get_search.json') as f:
            resp_data = f.read()
            responses.add(
                responses.GET,
                'https://api.twitter.com/1.1/search/tweets.json?count=15&result_type=mixed&q=python',
                body=resp_data,
                match_querystring=True,
                status=200)
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
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/search/tweets.json?q=twitter%20&result_type=recent&since=2014-07-19&count=100',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetSearch(raw_query="q=twitter%20&result_type=recent&since=2014-07-19&count=100")
        self.assertTrue([type(status) is twitter.Status for status in resp])
        self.assertTrue(['twitter' in status.text for status in resp])

    @responses.activate
    def testGetSearchGeocode(self):
        with open('testdata/get_search_geocode.json') as f:
            resp_data = f.read()
            responses.add(
                responses.GET,
                'https://api.twitter.com/1.1/search/tweets.json?result_type=mixed&count=15&geocode=37.781157%2C-122.398720%2C100mi&q=python',
                body=resp_data,
                match_querystring=True,
                status=200)
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
            responses.add(
                responses.GET,
                'https://api.twitter.com/1.1/users/search.json?count=20&q=python',
                body=resp_data,
                match_querystring=True,
                status=200)
        resp = self.api.GetUsersSearch(term='python')
        self.assertEqual(type(resp[0]), twitter.User)
        self.assertEqual(len(resp), 20)
        self.assertEqual(resp[0].id, 63873759)
        self.assertRaises(twitter.TwitterError,
                          lambda: self.api.GetUsersSearch(term='python',
                                                          count='test'))

    @responses.activate
    def testGetTrendsCurrent(self):
        with open('testdata/get_trends_current.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/trends/place.json?id=1',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetTrendsCurrent()
        self.assertTrue(type(resp[0]) is twitter.Trend)

    @responses.activate
    def testGetHomeTimeline(self):
        with open('testdata/get_home_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/home_timeline.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetHomeTimeline()
        status = resp[0]
        self.assertEqual(type(status), twitter.Status)
        self.assertEqual(status.id, 674674925823787008)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetHomeTimeline(count='literally infinity'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetHomeTimeline(count=4000))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetHomeTimeline(max_id='also infinity'))
        self.assertRaises(twitter.TwitterError,
                          lambda: self.api.GetHomeTimeline(
                              since_id='still infinity'))


        # TODO: Get data for this call against which we can test exclusions.
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/home_timeline.json?count=100&max_id=674674925823787008&trim_user=1',
            body=resp_data,
            match_querystring=True,
            status=200)
        self.assertTrue(self.api.GetHomeTimeline(count=100,
                                                 trim_user=True,
                                                 max_id=674674925823787008))

    @responses.activate
    def testGetUserTimeline(self):
        with open('testdata/get_user_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/user_timeline.json?user_id=673483',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetUserTimeline(user_id=673483)
        self.assertTrue(type(resp[0]) is twitter.Status)
        self.assertTrue(type(resp[0].user) is twitter.User)
        self.assertEqual(resp[0].user.id, 673483)

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=dewitt',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetUserTimeline(screen_name='dewitt')
        self.assertEqual(resp[0].id, 675055636267298821)
        self.assertTrue(resp)

    @responses.activate
    def testGetRetweets(self):
        with open('testdata/get_retweets.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/retweets/397.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetRetweets(statusid=397)
        self.assertTrue(type(resp[0]) is twitter.Status)
        self.assertTrue(type(resp[0].user) is twitter.User)

    @responses.activate
    def testGetRetweeters(self):
        with open('testdata/get_retweeters.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/retweeters/ids.json?id=397',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetRetweeters(status_id=397)
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is int)

    @responses.activate
    def testGetBlocks(self):
        with open('testdata/get_blocks_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/list.json?cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)
        with open('testdata/get_blocks_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/list.json?cursor=1524574483549312671',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetBlocks()
        self.assertTrue(
            isinstance(resp, list),
            "Expected resp type to be list, got {0}".format(type(resp)))
        self.assertTrue(
            isinstance(resp[0], twitter.User),
            "Expected type of first obj in resp to be twitter.User, got {0}".format(
                type(resp[0])))
        self.assertEqual(
            len(resp), 2,
            "Expected len of resp to be 2, got {0}".format(len(resp)))
        self.assertEqual(
            resp[0].screen_name, 'RedScareBot',
            "Expected screen_name of 1st blocked user to be RedScareBot, was {0}".format(
                resp[0].screen_name))
        self.assertEqual(
            resp[0].screen_name, 'RedScareBot',
            "Expected screen_name of 2nd blocked user to be RedScareBot, was {0}".format(
                resp[0].screen_name))

    @responses.activate
    def testGetBlocksPaged(self):
        with open('testdata/get_blocks_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/list.json?cursor=1524574483549312671',
            body=resp_data,
            match_querystring=True,
            status=200)
        ncur, pcur, resp = self.api.GetBlocksPaged(cursor=1524574483549312671)
        self.assertTrue(
            isinstance(resp, list),
            "Expected list, got {0}".format(type(resp)))
        self.assertTrue(
            isinstance(resp[0], twitter.User),
            "Expected twitter.User, got {0}".format(type(resp[0])))
        self.assertEqual(
            len(resp), 1,
            "Expected len of resp to be 1, got {0}".format(len(resp)))
        self.assertEqual(
            resp[0].screen_name, 'RedScareBot',
            "Expected username of blocked user to be RedScareBot, got {0}".format(
                resp[0].screen_name))

    @responses.activate
    def testGetBlocksIDs(self):
        with open('testdata/get_blocks_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/ids.json?cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)
        with open('testdata/get_blocks_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/ids.json?cursor=1524566179872860311',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetBlocksIDs()
        self.assertTrue(
            isinstance(resp, list),
            "Expected list, got {0}".format(type(resp)))
        self.assertTrue(
            isinstance(resp[0], int),
            "Expected list, got {0}".format(type(resp)))
        self.assertEqual(
            len(resp), 2,
            "Expected len of resp to be 2, got {0}".format(len(resp)))

    @responses.activate
    def testGetBlocksIDsPaged(self):
        with open('testdata/get_blocks_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/ids.json?cursor=1524566179872860311',
            body=resp_data,
            match_querystring=True,
            status=200)
        _, _, resp = self.api.GetBlocksIDsPaged(cursor=1524566179872860311)
        self.assertTrue(
            isinstance(resp, list),
            "Expected list, got {0}".format(type(resp)))
        self.assertTrue(
            isinstance(resp[0], int),
            "Expected list, got {0}".format(type(resp)))
        self.assertEqual(
            len(resp), 1,
            "Expected len of resp to be 1, got {0}".format(len(resp)))

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

    @responses.activate
    def testUsersLookup(self):
        with open('testdata/users_lookup.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/users/lookup.json?user_id=718443',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.UsersLookup(user_id=[718443])
        self.assertTrue(type(resp) is list)
        self.assertEqual(len(resp), 1)
        user = resp[0]
        self.assertTrue(type(user) is twitter.User)
        self.assertEqual(user.screen_name, 'kesuke')
        self.assertEqual(user.id, 718443)

    @responses.activate
    def testGetUser(self):
        with open('testdata/get_user.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/users/show.json?user_id=718443',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetUser(user_id=718443)
        self.assertTrue(type(resp) is twitter.User)
        self.assertEqual(resp.screen_name, 'kesuke')
        self.assertEqual(resp.id, 718443)

    @responses.activate
    def testGetDirectMessages(self):
        with open('testdata/get_direct_messages.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/direct_messages.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetDirectMessages()
        self.assertTrue(type(resp) is list)
        direct_message = resp[0]
        self.assertTrue(type(direct_message) is twitter.DirectMessage)
        self.assertEqual(direct_message.id, 678629245946433539)

    @responses.activate
    def testGetSentDirectMessages(self):
        with open('testdata/get_sent_direct_messages.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/direct_messages/sent.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetSentDirectMessages()
        self.assertTrue(type(resp) is list)
        direct_message = resp[0]
        self.assertTrue(type(direct_message) is twitter.DirectMessage)
        self.assertEqual(direct_message.id, 678629283007303683)
        self.assertTrue([dm.sender_screen_name == 'notinourselves' for dm in resp])

    @responses.activate
    def testGetFavorites(self):
        with open('testdata/get_favorites.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/favorites/list.json?include_entities=True',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetFavorites()
        self.assertTrue(type(resp) is list)
        fav = resp[0]
        self.assertEqual(fav.id, 677180133447372800)
        self.assertIn("Extremely", fav.text)

    @responses.activate
    def testGetMentions(self):
        with open('testdata/get_mentions.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/mentions_timeline.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetMentions()
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(mention) is twitter.Status for mention in resp])
        self.assertEqual(resp[0].id, 676148312349609985)

    @responses.activate
    def testGetListTimeline(self):
        with open('testdata/get_list_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/statuses.json?slug=space-bots&owner_screen_name=inky',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListTimeline(list_id=None,
                                        slug='space-bots',
                                        owner_screen_name='inky')
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(status) is twitter.Status for status in resp])
        self.assertEqual(resp[0].id, 677891843946766336)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetListTimeline(
                list_id=None,
                slug=None,
                owner_id=None))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetListTimeline(
                list_id=None,
                slug=None,
                owner_screen_name=None))

    @responses.activate
    def testPostUpdate(self):
        with open('testdata/post_update.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/statuses/update.json',
            body=resp_data,
            status=200)
        post = self.api.PostUpdate(
            status="blah Longitude coordinate of the tweet in degrees.")
        self.assertTrue(type(post) is twitter.Status)
        self.assertEqual(
            post.text, "blah Longitude coordinate of the tweet in degrees.")
        self.assertTrue(post.geo is None)
        self.assertEqual(post.user.screen_name, 'notinourselves')

    @responses.activate
    def testPostUpdateExtraParams(self):
        with open('testdata/post_update_extra_params.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/statuses/update.json',
            body=resp_data,
            status=200)
        post = self.api.PostUpdate(
            status="Not a dupe. Longitude coordinate of the tweet in degrees.",
            in_reply_to_status_id=681496308251754496,
            latitude=37.781157,
            longitude=-122.398720,
            place_id="1",
            display_coordinates=True,
            trim_user=True)
        self.assertEqual(post.in_reply_to_status_id, 681496308251754496)
        self.assertIsNotNone(post.coordinates)

    @responses.activate
    def testVerifyCredentials(self):
        with open('testdata/verify_credentials.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{0}/account/verify_credentials.json'.format(self.api.base_url),
            body=resp_data,
            status=200)

        resp = self.api.VerifyCredentials()
        self.assertEqual(type(resp), twitter.User)
        self.assertEqual(resp.name, 'notinourselves')

    @responses.activate
    def testUpdateBanner(self):
        responses.add(
            responses.POST,
            '{0}/account/update_profile_banner.json'.format(self.api.base_url),
            body=b'',
            status=201
        )
        resp = self.api.UpdateBanner(image='testdata/168NQ.jpg')
        self.assertTrue(resp)

    @responses.activate
    def testUpdateBanner422Error(self):
        responses.add(
            responses.POST,
            '{0}/account/update_profile_banner.json'.format(self.api.base_url),
            body=b'',
            status=422
        )
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.UpdateBanner(image='testdata/168NQ.jpg')
        )
        try:
            self.api.UpdateBanner(image='testdata/168NQ.jpg')
        except twitter.TwitterError as e:
            self.assertTrue("The image could not be resized or is too large." in str(e))

    @responses.activate
    def testUpdateBanner400Error(self):
        responses.add(
            responses.POST,
            '{0}/account/update_profile_banner.json'.format(self.api.base_url),
            body=b'',
            status=400
        )
        try:
            self.api.UpdateBanner(image='testdata/168NQ.jpg')
        except twitter.TwitterError as e:
            self.assertTrue("Image data could not be processed" in str(e))

    @responses.activate
    def testGetMemberships(self):
        with open('testdata/get_memberships.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/memberships.json?cursor=-1&count=20',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetMemberships()
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(lst) is twitter.List for lst in resp])
        self.assertEqual(resp[0].id, 210635540)

    @responses.activate
    def testGetListsList(self):
        with open('testdata/get_lists_list.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/list.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListsList()
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(lst) is twitter.List for lst in resp])
        self.assertEqual(resp[0].id, 189643778)

        with open('testdata/get_lists_list_screen_name.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/list.json?screen_name=inky',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListsList(screen_name='inky')
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(lst) is twitter.List for lst in resp])
        self.assertEqual(resp[0].id, 224581495)

        with open('testdata/get_lists_list_user_id.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/list.json?user_id=13148',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListsList(user_id=13148)
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(lst) is twitter.List for lst in resp])
        self.assertEqual(resp[0].id, 224581495)

    @responses.activate
    def testGetLists(self):
        with open('testdata/get_lists.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/ownerships.json?cursor=-1&count=20',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetLists()
        self.assertTrue(resp)
        lst = resp[0]
        self.assertEqual(lst.id, 229581524)
        self.assertTrue(type(lst), twitter.List)
        self.assertEqual(lst.full_name, "@notinourselves/test")
        self.assertEqual(lst.slug, "test")

    @responses.activate
    def testGetListMembers(self):
        with open('testdata/get_list_members_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/members.json?count=100&include_entities=False&skip_status=False&list_id=93527328&cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)

        with open('testdata/get_list_members_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/members.json?count=100&include_entities=False&skip_status=False&cursor=4611686020936348428&list_id=93527328',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListMembers(list_id=93527328)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(resp[0].id, 4048395140)

    @responses.activate
    def testGetListMembersPaged(self):
        with open('testdata/get_list_members_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/members.json?count=100&include_entities=True&skip_status=False&cursor=4611686020936348428&list_id=93527328',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListMembersPaged(list_id=93527328, cursor=4611686020936348428)
        self.assertTrue([isinstance(u, twitter.User) for u in resp])

        with open('testdata/get_list_members_extra_params.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/members.json?count=100&skip_status=True&include_entities=False&cursor=4611686020936348428&list_id=93527328',
            body=resp_data,
            match_querystring=True,
            status=200)
        _, _, resp = self.api.GetListMembersPaged(list_id=93527328,
                                            cursor=4611686020936348428,
                                            skip_status=True,
                                            include_entities=False,
                                            count=100)
        self.assertFalse(resp[0].status)

    @responses.activate
    def testGetListTimeline(self):
        with open('testdata/get_list_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/statuses.json?&list_id=229581524',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListTimeline(list_id=229581524)
        self.assertTrue(type(resp[0]) is twitter.Status)

        with open('testdata/get_list_timeline_max_since.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/statuses.json?since_id=692829211019575296&owner_screen_name=notinourselves&slug=test&max_id=692980243339071488',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListTimeline(slug='test',
                                        owner_screen_name='notinourselves',
                                        max_id=692980243339071488,
                                        since_id=692829211019575296)
        self.assertTrue([isinstance(s, twitter.Status) for s in resp])
        self.assertEqual(len(resp), 7)
        self.assertTrue([s.id >= 692829211019575296 for s in resp])
        self.assertTrue([s.id <= 692980243339071488 for s in resp])

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetListTimeline(slug='test'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetListTimeline())

        # 4012966701
        with open('testdata/get_list_timeline_count_rts_ent.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/statuses.json?count=13&slug=test&owner_id=4012966701&include_rts=False&include_entities=False',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListTimeline(slug='test',
                                        owner_id=4012966701,
                                        count=13,
                                        include_entities=False,
                                        include_rts=False)
        self.assertEqual(len(resp), 13)
        # TODO: test the other exclusions, but my bots don't retweet and
        # twitter.status.Status doesn't include entities node?

    @responses.activate
    def testCreateList(self):
        with open('testdata/post_create_list.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/lists/create.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.CreateList(
            name='test2',
            mode='private',
            description='test for python-twitter')
        self.assertEqual(resp.id, 233452137)
        self.assertEqual(resp.description, 'test for python-twitter')
        self.assertEqual(resp.mode, 'private')

    @responses.activate
    def testDestroyList(self):
        with open('testdata/post_destroy_list.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/lists/destroy.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.DestroyList(list_id=233452137)
        self.assertEqual(resp.id, 233452137)
        self.assertEqual(resp.member_count, 0)

    @responses.activate
    def testCreateSubscription(self):
        with open('testdata/post_create_subscription.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/lists/subscribers/create.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.CreateSubscription(list_id=225486809)
        self.assertEqual(resp.id, 225486809)
        self.assertEqual(resp.name, 'my-bots')

    @responses.activate
    def testDestroySubscription(self):
        with open('testdata/post_destroy_subscription.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/lists/subscribers/destroy.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.DestroySubscription(list_id=225486809)
        self.assertEqual(resp.id, 225486809)
        self.assertEqual(resp.name, 'my-bots')

    @responses.activate
    def testShowSubscription(self):
        # User not a subscriber to the list.
        with open('testdata/get_show_subscription_not_subscriber.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/subscribers/show.json?user_id=4040207472&list_id=189643778',
            body=resp_data,
            match_querystring=True,
            status=200)
        try:
            self.api.ShowSubscription(list_id=189643778, user_id=4040207472)
        except twitter.TwitterError as e:
            self.assertIn(
                "The specified user is not a subscriber of this list.",
                str(e.message))

        # User is a subscriber to list
        with open('testdata/get_show_subscription.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/subscribers/show.json?list_id=189643778&screen_name=__jcbl__',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.ShowSubscription(list_id=189643778,
                                         screen_name='__jcbl__')
        self.assertEqual(resp.id, 372018022)
        self.assertEqual(resp.screen_name, '__jcbl__')
        self.assertTrue(resp.status)

        # User is subscriber, using extra params
        with open('testdata/get_show_subscription_extra_params.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/subscribers/show.json?include_entities=True&list_id=18964377&skip_status=True&screen_name=__jcbl__',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.ShowSubscription(list_id=18964377,
                                         screen_name='__jcbl__',
                                         include_entities=True,
                                         skip_status=True)
        self.assertFalse(resp.status)

    @responses.activate
    def testGetSubscriptions(self):
        with open('testdata/get_get_subscriptions.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/subscriptions.json?count=20&cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetSubscriptions()
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0].name, 'space bots')

    @responses.activate
    def testGetSubscriptionsSN(self):
        with open('testdata/get_get_subscriptions_uid.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/subscriptions.json?count=20&cursor=-1&screen_name=inky',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetSubscriptions(screen_name='inky')
        self.assertEqual(len(resp), 20)
        self.assertTrue([isinstance(l, twitter.List) for l in resp])

    @responses.activate
    def testGetMemberships(self):
        with open('testdata/get_get_memberships.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/memberships.json?count=20&cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetMemberships()
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0].name, 'my-bots')

        with open('testdata/get_get_memberships_himawari8bot.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/memberships.json?count=20&cursor=-1&screen_name=himawari8bot',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetMemberships(screen_name='himawari8bot')
        self.assertEqual(len(resp), 20)
        self.assertTrue([isinstance(lst, twitter.List) for lst in resp])

    @responses.activate
    def testCreateListsMember(self):
        with open('testdata/post_create_lists_member.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/lists/members/create.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.CreateListsMember(list_id=229581524, user_id=372018022)
        self.assertTrue(isinstance(resp, twitter.List))
        self.assertEqual(resp.name, 'test')
        self.assertEqual(resp.member_count, 2)

    @responses.activate
    def testCreateListsMemberMultiple(self):
        with open('testdata/post_create_lists_member_multiple.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/lists/members/create_all.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.CreateListsMember(list_id=229581524,
                                          user_id=[372018022, 4040207472])
        self.assertTrue(isinstance(resp, twitter.List))
        self.assertEqual(resp.name, 'test')
        self.assertEqual(resp.member_count, 3)

    @responses.activate
    def testDestroyListsMember(self):
        with open('testdata/post_destroy_lists_member.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/lists/members/destroy.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.DestroyListsMember(list_id=229581524, user_id=372018022)
        self.assertTrue(isinstance(resp, twitter.List))
        self.assertEqual(resp.name, 'test')
        self.assertEqual(resp.member_count, 1)

    @responses.activate
    def testDestroyListsMemberMultiple(self):
        with open('testdata/post_destroy_lists_member_multiple.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/lists/members/destroy_all.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.DestroyListsMember(list_id=229581524,
                                           user_id=[372018022, 4040207472])
        self.assertEqual(resp.member_count, 0)
        self.assertEqual(resp.name, 'test')
        self.assertTrue(isinstance(resp, twitter.List))

    @responses.activate
    def testPostUpdateWithMedia(self):
        # API will first make a POST request to upload the file.
        with open('testdata/post_upload_media_simple.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://upload.twitter.com/1.1/media/upload.json',
            body=resp_data,
            match_querystring=True,
            status=200)

        # Then the POST request to post a status with the media id attached.
        with open('testdata/post_update_media_id.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/statuses/update.json?media_ids=697007311538229248',
            body=resp_data,
            match_querystring=True,
            status=200)

        # Local file
        resp = self.api.PostUpdate(media='testdata/168NQ.jpg', status='test')
        self.assertEqual(697007311538229248, resp.AsDict()['media'][0].id)
        self.assertEqual(resp.text, "hi this is a test for media uploads with statuses https://t.co/FHgqb6iLOX")

        # File object
        with open('testdata/168NQ.jpg', 'rb') as f:
            resp = self.api.PostUpdate(media=[f], status='test')
        self.assertEqual(697007311538229248, resp.AsDict()['media'][0].id)
        self.assertEqual(resp.text, "hi this is a test for media uploads with statuses https://t.co/FHgqb6iLOX")

        # Media ID as int
        resp = self.api.PostUpdate(media=697007311538229248, status='test')

        # Media ID as list of ints
        resp = self.api.PostUpdate(media=[697007311538229248], status='test')
        responses.add(
            responses.POST,
            "https://api.twitter.com/1.1/statuses/update.json?media_ids=697007311538229248,697007311538229249",
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.PostUpdate(
            media=[697007311538229248, 697007311538229249], status='test')

    @responses.activate
    def testLookupFriendship(self):
        with open('testdata/get_friendships_lookup_none.json') as f:
            resp_data = f.read()

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?user_id=12',
            body=resp_data,
            match_querystring=True,
            status=200)

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?user_id=12,6385432',
            body=resp_data,
            match_querystring=True,
            status=200)
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?screen_name=jack',
            body=resp_data,
            match_querystring=True,
            status=200)
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?screen_name=jack,dickc',
            body=resp_data,
            match_querystring=True,
            status=200)

        resp = self.api.LookupFriendship(user_id=12)
        self.assertTrue(isinstance(resp, list))
        self.assertTrue(isinstance(resp[0], twitter.UserStatus))
        self.assertEqual(resp[0].following, False)
        self.assertEqual(resp[0].followed_by, False)

        # If any of the following produce an unexpect result, the test will
        # fail on a request to a URL that hasn't been set by responses:
        test_user = twitter.User(id=12, screen_name='jack')
        test_user2 = twitter.User(id=6385432, screen_name='dickc')

        resp = self.api.LookupFriendship(screen_name='jack')
        resp = self.api.LookupFriendship(screen_name=['jack'])
        resp = self.api.LookupFriendship(screen_name=test_user)
        resp = self.api.LookupFriendship(screen_name=[test_user, test_user2])

        resp = self.api.LookupFriendship(user_id=12)
        resp = self.api.LookupFriendship(user_id=[12])
        resp = self.api.LookupFriendship(user_id=test_user)
        resp = self.api.LookupFriendship(user_id=[test_user, test_user2])

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.LookupFriendship())

    @responses.activate
    def testLookupFriendshipMute(self):
        with open('testdata/get_friendships_lookup_muting.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?screen_name=dickc',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.LookupFriendship(screen_name='dickc')
        self.assertEqual(resp[0].blocking, False)
        self.assertEqual(resp[0].muting, True)

    @responses.activate
    def testLookupFriendshipBlockMute(self):
        with open('testdata/get_friendships_lookup_muting_blocking.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?screen_name=dickc',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.LookupFriendship(screen_name='dickc')
        self.assertEqual(resp[0].muting, True)
        self.assertEqual(resp[0].blocking, True)
