# encoding: utf-8
from __future__ import unicode_literals, print_function

import json
import os
import re
import sys
from tempfile import NamedTemporaryFile
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import warnings

import twitter

import responses
from responses import GET, POST

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
        responses.add(GET, DEFAULT_URL, body='')

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
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetHelpConfiguration()
        self.assertEqual(resp.get('short_url_length_https'), 23)

    @responses.activate
    def testGetShortUrlLength(self):
        with open('testdata/get_help_configuration.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetShortUrlLength()
        self.assertEqual(resp, 23)
        resp = self.api.GetShortUrlLength(https=True)
        self.assertEqual(resp, 23)

    @responses.activate
    def testGetSearch(self):
        with open('testdata/get_search.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetSearch(raw_query="q=twitter%20&result_type=recent&since=2014-07-19&count=100")
        self.assertTrue([type(status) is twitter.Status for status in resp])
        self.assertTrue(['twitter' in status.text for status in resp])

    @responses.activate
    def testGetSearchGeocode(self):
        with open('testdata/get_search_geocode.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetTrendsCurrent()
        self.assertTrue(type(resp[0]) is twitter.Trend)

    @responses.activate
    def testGetHomeTimeline(self):
        with open('testdata/get_home_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            GET, 'https://api.twitter.com/1.1/statuses/home_timeline.json?tweet_mode=compat',
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

    @responses.activate
    def testGetHomeTimelineWithExclusions(self):
        with open('testdata/get_home_timeline.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)
        self.assertTrue(self.api.GetHomeTimeline(count=100,
                                                 trim_user=True,
                                                 max_id=674674925823787008))

    @responses.activate
    def testGetUserTimelineByUserID(self):
        with open('testdata/get_user_timeline.json') as f:
            resp_data = f.read()
        responses.add(responses.GET, DEFAULT_URL, body=resp_data, status=200)
        resp = self.api.GetUserTimeline(user_id=673483)
        self.assertTrue(type(resp[0]) is twitter.Status)
        self.assertTrue(type(resp[0].user) is twitter.User)
        self.assertEqual(resp[0].user.id, 673483)

    @responses.activate
    def testGetUserTimelineByScreenName(self):
        with open('testdata/get_user_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            GET, DEFAULT_URL, body=resp_data)
        resp = self.api.GetUserTimeline(screen_name='dewitt')
        self.assertEqual(resp[0].id, 675055636267298821)
        self.assertTrue(resp)

    @responses.activate
    def testGetRetweets(self):
        with open('testdata/get_retweets.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetRetweets(statusid=397)
        self.assertTrue(type(resp[0]) is twitter.Status)
        self.assertTrue(type(resp[0].user) is twitter.User)

    @responses.activate
    def testGetRetweetsCount(self):
        with open('testdata/get_retweets_count.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetRetweets(statusid=312, count=63)
        self.assertTrue(len(resp), 63)

    @responses.activate
    def testGetRetweeters(self):
        with open('testdata/get_retweeters.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetRetweeters(status_id=397)
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is int)

    @responses.activate
    def testGetBlocks(self):
        with open('testdata/get_blocks_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/list.json?cursor=-1&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)
        with open('testdata/get_blocks_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/list.json?cursor=1524574483549312671&tweet_mode=compat',
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
            'https://api.twitter.com/1.1/blocks/ids.json?cursor=-1&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)
        with open('testdata/get_blocks_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/ids.json?cursor=1524566179872860311&tweet_mode=compat',
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
            GET,
            'https://api.twitter.com/1.1/friends/ids.json?count=5000&cursor=-1&stringify_ids=False&screen_name=EricHolthaus&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining friends
        with open('testdata/get_friend_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friends/ids.json?stringify_ids=False&count=5000&cursor=1417903878302254556&screen_name=EricHolthaus&tweet_mode=compat',
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
        responses.add(responses.GET, DEFAULT_URL, body=resp_data, status=200)

        ncursor, pcursor, resp = self.api.GetFriendIDsPaged(screen_name='EricHolthaus')
        self.assertLessEqual(len(resp), 5000)
        self.assertTrue(ncursor)
        self.assertFalse(pcursor)

    @responses.activate
    def testGetFriendsPaged(self):
        with open('testdata/get_friends_paged.json') as f:
            resp_data = f.read()
        responses.add(responses.GET, DEFAULT_URL, body=resp_data, status=200)

        ncursor, pcursor, resp = self.api.GetFriendsPaged(screen_name='codebear', count=200)
        self.assertEqual(ncursor, 1494734862149901956)
        self.assertEqual(pcursor, 0)
        self.assertEqual(len(resp), 200)
        self.assertTrue(type(resp[0]) is twitter.User)

    @responses.activate
    def testGetFriendsPagedUID(self):
        with open('testdata/get_friends_paged_uid.json') as f:
            resp_data = f.read()
        responses.add(responses.GET, DEFAULT_URL, body=resp_data, status=200)

        ncursor, pcursor, resp = self.api.GetFriendsPaged(user_id=12, count=200)
        self.assertEqual(ncursor, 1510410423140902959)
        self.assertEqual(pcursor, 0)
        self.assertEqual(len(resp), 200)
        self.assertTrue(type(resp[0]) is twitter.User)

    @responses.activate
    def testGetFriendsAdditionalParams(self):
        with open('testdata/get_friends_paged_additional_params.json') as f:
            resp_data = f.read()
        responses.add(responses.GET, DEFAULT_URL, body=resp_data, status=200)

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
            endpoint = 'https://api.twitter.com/1.1/friends/list.json?count=200&tweet_mode=compat&include_user_entities=True&screen_name=codebear&skip_status=False&cursor={0}'.format(cursor)
            responses.add(GET, endpoint, body=resp_data, match_querystring=True)
            cursor = json.loads(resp_data)['next_cursor']

        resp = self.api.GetFriends(screen_name='codebear')
        self.assertEqual(len(resp), 819)

    @responses.activate
    def testGetFriendsWithLimit(self):
        with open('testdata/get_friends_0.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
            'https://api.twitter.com/1.1/followers/ids.json?tweet_mode=compat&cursor=-1&stringify_ids=False&count=5000&screen_name=GirlsMakeGames',
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining followers
        with open('testdata/get_follower_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/followers/ids.json?tweet_mode=compat&count=5000&screen_name=GirlsMakeGames&cursor=1482201362283529597&stringify_ids=False',
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
            lambda: self.api.GetFollowerIDs(total_count='infinity'))

    @responses.activate
    def testGetFollowers(self):
        # First request for first 200 followers
        with open('testdata/get_followers_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/list.json?tweet_mode=compat&include_user_entities=True&count=200&screen_name=himawari8bot&skip_status=False&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining followers
        with open('testdata/get_followers_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/list.json?tweet_mode=compat&include_user_entities=True&skip_status=False&count=200&screen_name=himawari8bot&cursor=1516850034842747602'.format(
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
            'https://api.twitter.com/1.1/followers/ids.json?tweet_mode=compat&count=5000&stringify_ids=False&cursor=-1&screen_name=himawari8bot',
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
            'https://api.twitter.com/1.1/followers/ids.json?tweet_mode=compat&count=5000&stringify_ids=True&user_id=12&cursor=-1',
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetUser(user_id=718443)
        self.assertTrue(type(resp) is twitter.User)
        self.assertEqual(resp.screen_name, 'kesuke')
        self.assertEqual(resp.id, 718443)

    @responses.activate
    def testGetDirectMessages(self):
        with open('testdata/get_direct_messages.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetDirectMessages()
        self.assertTrue(type(resp) is list)
        direct_message = resp[0]
        self.assertTrue(type(direct_message) is twitter.DirectMessage)
        self.assertEqual(direct_message.id, 678629245946433539)

    @responses.activate
    def testGetSentDirectMessages(self):
        with open('testdata/get_sent_direct_messages.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetFavorites()
        self.assertTrue(type(resp) is list)
        fav = resp[0]
        self.assertEqual(fav.id, 677180133447372800)
        self.assertIn("Extremely", fav.text)

    @responses.activate
    def testGetMentions(self):
        with open('testdata/get_mentions.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetMentions()
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(mention) is twitter.Status for mention in resp])
        self.assertEqual(resp[0].id, 676148312349609985)

    @responses.activate
    def testGetListTimeline(self):
        with open('testdata/get_list_timeline.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetListTimeline(list_id=None,
                                        slug='space-bots',
                                        owner_screen_name='inky')
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(status) is twitter.Status for status in resp])
        self.assertEqual(resp[0].id, 693191602957852676)

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
            POST,
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
            POST,
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.VerifyCredentials()
        self.assertEqual(type(resp), twitter.User)
        self.assertEqual(resp.name, 'notinourselves')

    @responses.activate
    def testVerifyCredentialsIncludeEmail(self):
        with open('testdata/get_verify_credentials_include_email.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.VerifyCredentials(skip_status=True, include_email=True)
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.email, 'test@example.com')

    @responses.activate
    def testUpdateBanner(self):
        responses.add(
            POST,
            '{0}/account/update_profile_banner.json'.format(self.api.base_url),
            body=b'',
            status=201
        )
        resp = self.api.UpdateBanner(image='testdata/168NQ.jpg')
        self.assertTrue(resp)

    @responses.activate
    def testUpdateBanner422Error(self):
        responses.add(
            POST,
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
            POST,
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
            'https://api.twitter.com/1.1/lists/list.json?tweet_mode=compat',
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
            'https://api.twitter.com/1.1/lists/list.json?tweet_mode=compat&screen_name=inky',
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
            'https://api.twitter.com/1.1/lists/list.json?tweet_mode=compat&user_id=13148',
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

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
            'https://api.twitter.com/1.1/lists/members.json?count=100&include_entities=False&skip_status=False&list_id=93527328&cursor=-1&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)

        with open('testdata/get_list_members_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/members.json?list_id=93527328&skip_status=False&include_entities=False&count=100&tweet_mode=compat&cursor=4611686020936348428',
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
            'https://api.twitter.com/1.1/lists/members.json?count=100&include_entities=True&cursor=4611686020936348428&list_id=93527328&skip_status=False&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListMembersPaged(list_id=93527328, cursor=4611686020936348428)
        self.assertTrue([isinstance(u, twitter.User) for u in resp])

        with open('testdata/get_list_members_extra_params.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/members.json?count=100&tweet_mode=compat&cursor=4611686020936348428&list_id=93527328&skip_status=True&include_entities=False',
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
            'https://api.twitter.com/1.1/lists/statuses.json?&list_id=229581524&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListTimeline(list_id=229581524)
        self.assertTrue(type(resp[0]) is twitter.Status)

        with open('testdata/get_list_timeline_max_since.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/statuses.json?owner_screen_name=notinourselves&slug=test&max_id=692980243339071488&tweet_mode=compat&since_id=692829211019575296',
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
            'https://api.twitter.com/1.1/lists/statuses.json?include_rts=False&count=13&tweet_mode=compat&include_entities=False&slug=test&owner_id=4012966701',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListTimeline(slug='test',
                                        owner_id=4012966701,
                                        count=13,
                                        include_entities=False,
                                        include_rts=False)
        self.assertEqual(len(resp), 13)

    @responses.activate
    def testCreateList(self):
        with open('testdata/post_create_list.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
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
            POST,
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
            POST,
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
            POST,
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
            'https://api.twitter.com/1.1/lists/subscribers/show.json?tweet_mode=compat&user_id=4040207472&list_id=189643778',
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
            'https://api.twitter.com/1.1/lists/subscribers/show.json?list_id=189643778&tweet_mode=compat&screen_name=__jcbl__',
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
            'https://api.twitter.com/1.1/lists/subscribers/show.json?include_entities=True&tweet_mode=compat&list_id=18964377&skip_status=True&screen_name=__jcbl__',
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetSubscriptions()
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0].name, 'space bots')

    @responses.activate
    def testGetSubscriptionsSN(self):
        with open('testdata/get_get_subscriptions_uid.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetSubscriptions(screen_name='inky')
        self.assertEqual(len(resp), 20)
        self.assertTrue([isinstance(l, twitter.List) for l in resp])

    @responses.activate
    def testGetMemberships(self):
        with open('testdata/get_get_memberships.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/memberships.json?count=20&cursor=-1&tweet_mode=compat',
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
            'https://api.twitter.com/1.1/lists/memberships.json?count=20&cursor=-1&screen_name=himawari8bot&tweet_mode=compat',
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
            POST,
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
            POST,
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
            POST,
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
            POST,
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
            POST,
            'https://upload.twitter.com/1.1/media/upload.json',
            body=resp_data,
            match_querystring=True,
            status=200)

        # Then the POST request to post a status with the media id attached.
        with open('testdata/post_update_media_id.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            'https://api.twitter.com/1.1/statuses/update.json?media_ids=697007311538229248',
            body=resp_data,
            match_querystring=True,
            status=200)

        # Local file
        resp = self.api.PostUpdate(media='testdata/168NQ.jpg', status='test')
        self.assertEqual(697007311538229248, resp.AsDict()['media'][0]['id'])
        self.assertEqual(resp.text, "hi this is a test for media uploads with statuses https://t.co/FHgqb6iLOX")

        # File object
        with open('testdata/168NQ.jpg', 'rb') as f:
            resp = self.api.PostUpdate(media=[f], status='test')
        self.assertEqual(697007311538229248, resp.AsDict()['media'][0]['id'])
        self.assertEqual(resp.text, "hi this is a test for media uploads with statuses https://t.co/FHgqb6iLOX")

        # Media ID as int
        resp = self.api.PostUpdate(media=697007311538229248, status='test')

        # Media ID as list of ints
        resp = self.api.PostUpdate(media=[697007311538229248], status='test')
        responses.add(
            POST,
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
            'https://api.twitter.com/1.1/friendships/lookup.json?user_id=12&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?user_id=12,6385432&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?screen_name=jack&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friendships/lookup.json?screen_name=jack,dickc&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)

        resp = self.api.LookupFriendship(user_id=12)
        self.assertTrue(isinstance(resp, list))
        self.assertTrue(isinstance(resp[0], twitter.UserStatus))
        self.assertEqual(resp[0].following, False)
        self.assertEqual(resp[0].followed_by, False)

        # If any of the following produce an unexpected result, the test will
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
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.LookupFriendship(screen_name='dickc')
        self.assertEqual(resp[0].blocking, False)
        self.assertEqual(resp[0].muting, True)

    @responses.activate
    def testLookupFriendshipBlockMute(self):
        with open('testdata/get_friendships_lookup_muting_blocking.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.LookupFriendship(screen_name='dickc')
        self.assertEqual(resp[0].muting, True)
        self.assertEqual(resp[0].blocking, True)

    @responses.activate
    def testPostMediaMetadata(self):
        responses.add(
            POST,
            'https://upload.twitter.com/1.1/media/metadata/create.json',
            body=b'',
            status=200)
        resp = self.api.PostMediaMetadata(media_id=718561981427396608, alt_text='test')

        # At the moment, all we can do is test if the method call works. The response
        # body should be blank, with a 200 status on success.
        self.assertTrue(resp)

    @responses.activate
    def testGetStatusWithExtAltText(self):
        with open('testdata/get_status_ext_alt.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetStatus(status_id=724441953534877696)
        self.assertEqual(resp.media[0].ext_alt_text, "\u201cJon Snow is dead.\u2026\u201d from \u201cGAME OF THRONES SEASON 6 EPISODES\u201d by HBO PR.")

    @responses.activate
    def testGetStatus(self):
        with open('testdata/get_status.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetStatus(status_id=397)

        self.assertTrue(type(resp) is twitter.Status)
        self.assertEqual(resp.id, 397)
        self.assertEqual(resp.user.id, 12)
        self.assertFalse(resp != resp)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetStatus(status_id='test'))

    @responses.activate
    def testGetStatusExtraParams(self):
        with open('testdata/get_status_extra_params.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetStatus(status_id=397, trim_user=True, include_entities=False)
        self.assertFalse(resp.user.screen_name)

    @responses.activate
    def testGetStatusOembed(self):
        with open('testdata/get_status_oembed.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/oembed.json?tweet_mode=compat&id=397',
            body=resp_data,
            match_querystring=True,
            status=200)
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/oembed.json?tweet_mode=compat&url=https://twitter.com/jack/statuses/397',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp_id = self.api.GetStatusOembed(status_id=397)
        self.assertEqual(resp_id['url'], 'https://twitter.com/jack/statuses/397')
        self.assertEqual(resp_id['provider_url'], 'https://twitter.com')
        self.assertEqual(resp_id['provider_name'], 'Twitter')

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetStatusOembed(status_id='test'))

        resp_url = self.api.GetStatusOembed(url="https://twitter.com/jack/statuses/397")
        self.assertEqual(resp_id, resp_url)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetStatusOembed(status_id=None, url=None))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetStatusOembed(status_id=397, align='test'))

    @responses.activate
    def testGetMutes(self):
        # First iteration of the loop to get all the user's mutes
        with open('testdata/get_mutes_users_list_loop_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/mutes/users/list.json?cursor=-1&tweet_mode=compat&include_entities=True',
            body=resp_data,
            match_querystring=True,
            status=200)

        # Last interation of that loop.
        with open('testdata/get_mutes_users_list_loop_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/mutes/users/list.json?cursor=1535206520056388207&include_entities=True&tweet_mode=compat',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetMutes(include_entities=True)
        self.assertEqual(len(resp), 82)
        self.assertTrue(isinstance(resp[0], twitter.User))

    @responses.activate
    def testGetMutesIDs(self):
        # First iteration of the loop to get all the user's mutes
        with open('testdata/get_mutes_users_ids_loop_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/mutes/users/ids.json?tweet_mode=compat&cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)

        # Last interation of that loop.
        with open('testdata/get_mutes_users_ids_loop_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/mutes/users/ids.json?tweet_mode=compat&cursor=1535206520056565155',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetMutesIDs()
        self.assertEqual(len(resp), 82)
        self.assertTrue(isinstance(resp[0], int))

    @responses.activate
    def testCreateBlock(self):
        with open('testdata/post_blocks_create.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            'https://api.twitter.com/1.1/blocks/create.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.CreateBlock(screen_name='jack')
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.screen_name, 'jack')

        resp = self.api.CreateBlock(user_id=12)
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.id, 12)

    @responses.activate
    def testDestroyBlock(self):
        with open('testdata/post_blocks_destroy.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            'https://api.twitter.com/1.1/blocks/destroy.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.DestroyBlock(screen_name='jack')
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.screen_name, 'jack')

        resp = self.api.DestroyBlock(user_id=12)
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.id, 12)

    @responses.activate
    def testCreateMute(self):
        with open('testdata/post_mutes_users_create.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            'https://api.twitter.com/1.1/mutes/users/create.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.CreateMute(screen_name='jack')
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.screen_name, 'jack')

        resp = self.api.CreateMute(user_id=12)
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.id, 12)

    @responses.activate
    def testDestroyMute(self):
        with open('testdata/post_mutes_users_destroy.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            'https://api.twitter.com/1.1/mutes/users/destroy.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.DestroyMute(screen_name='jack')
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.screen_name, 'jack')

        resp = self.api.DestroyMute(user_id=12)
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertEqual(resp.id, 12)

    @responses.activate
    def testMuteBlockParamsAndErrors(self):
        # Basic type/error checking
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.CreateMute(user_id='test'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.CreateMute())

        with open('testdata/post_mutes_users_create_skip_status.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            'https://api.twitter.com/1.1/mutes/users/create.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.CreateMute(screen_name='jack', skip_status=True)
        self.assertTrue(isinstance(resp, twitter.User))
        self.assertFalse(resp.status)

    @responses.activate
    def testPostUploadMediaChunkedInit(self):
        with open('testdata/post_upload_chunked_INIT.json') as f:
            resp_data = f.read()
        responses.add(POST, DEFAULT_URL, body=resp_data, status=200)

        with open('testdata/corgi.gif', 'rb') as fp:
            resp = self.api._UploadMediaChunkedInit(fp)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(resp[0], 737956420046356480)

    @responses.activate
    def testPostUploadMediaChunkedAppend(self):
        media_fp, filename, _, _ = twitter.twitter_utils.parse_media_file(
            'testdata/corgi.gif')
        responses.add(POST, DEFAULT_URL, body='', status=200)

        resp = self.api._UploadMediaChunkedAppend(media_id=737956420046356480,
                                                  media_fp=media_fp,
                                                  filename=filename)
        self.assertEqual(len(responses.calls), 7)
        self.assertTrue(resp)

    @responses.activate
    def testPostUploadMediaChunkedAppendNonASCIIFilename(self):
        media_fp, filename, _, _ = twitter.twitter_utils.parse_media_file(
            'testdata/corgi.gif')
        filename = "عَرَبِيّ"
        responses.add(responses.POST, DEFAULT_URL, body='', status=200)

        resp = self.api._UploadMediaChunkedAppend(media_id=737956420046356480,
                                                  media_fp=media_fp,
                                                  filename=filename)
        self.assertEqual(len(responses.calls), 7)

    @responses.activate
    def testPostUploadMediaChunkedFinalize(self):
        with open('testdata/post_upload_chunked_FINAL.json') as f:
            resp_data = f.read()
        responses.add(POST, DEFAULT_URL, body=resp_data, status=200)

        resp = self.api._UploadMediaChunkedFinalize(media_id=737956420046356480)
        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(resp)

    @responses.activate
    def testGetUserSuggestionCategories(self):
        with open('testdata/get_user_suggestion_categories.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetUserSuggestionCategories()
        self.assertTrue(type(resp[0]) is twitter.Category)

    @responses.activate
    def testGetUserSuggestion(self):
        with open('testdata/get_user_suggestion.json') as f:
            resp_data = f.read()
        responses.add(responses.GET, DEFAULT_URL, body=resp_data, status=200)

        category = twitter.Category(name='Funny', slug='funny', size=20)
        resp = self.api.GetUserSuggestion(category=category)
        self.assertTrue(type(resp[0]) is twitter.User)

    @responses.activate
    def testGetUserTimeSinceMax(self):
        with open('testdata/get_user_timeline_sincemax.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetUserTimeline(user_id=12, since_id=757782013914951680, max_id=758097930670645248)
        self.assertEqual(len(resp), 6)

    @responses.activate
    def testGetUserTimelineCount(self):
        with open('testdata/get_user_timeline_count.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.GetUserTimeline(user_id=12, count=63)
        self.assertEqual(len(resp), 63)

    @responses.activate
    def testDestroyStatus(self):
        with open('testdata/post_destroy_status.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            DEFAULT_URL,
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.DestroyStatus(status_id=746507834003578880)
        self.assertTrue(isinstance(resp, twitter.models.Status))
        self.assertEqual(resp.id, 746507834003578880)

    @responses.activate
    def testCreateFavorite(self):
        with open('testdata/post_create_favorite.json') as f:
            resp_data = f.read()
        responses.add(POST, DEFAULT_URL, body=resp_data, status=200)

        resp = self.api.CreateFavorite(status_id=757283981683412992)
        self.assertEqual(resp.id, 757283981683412992)
        status = twitter.models.Status(id=757283981683412992)
        resp = self.api.CreateFavorite(status)
        self.assertEqual(resp.id, 757283981683412992)

    @responses.activate
    def testDestroyFavorite(self):
        with open('testdata/post_destroy_favorite.json') as f:
            resp_data = f.read()
        responses.add(POST, DEFAULT_URL, body=resp_data, status=200)

        resp = self.api.DestroyFavorite(status_id=757283981683412992)
        self.assertEqual(resp.id, 757283981683412992)
        status = twitter.models.Status(id=757283981683412992)
        resp = self.api.DestroyFavorite(status)
        self.assertEqual(resp.id, 757283981683412992)

    @responses.activate
    def testPostDirectMessage(self):
        with open('testdata/post_post_direct_message.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            DEFAULT_URL,
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.PostDirectMessage(text="test message", user_id=372018022)
        self.assertEqual(resp.text, "test message")

        resp = self.api.PostDirectMessage(text="test message", screen_name="__jcbl__")
        self.assertEqual(resp.sender_id, 4012966701)
        self.assertEqual(resp.recipient_id, 372018022)
        self.assertTrue(resp._json)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.PostDirectMessage(text="test message"))

    @responses.activate
    def testDestroyDirectMessage(self):
        with open('testdata/post_destroy_direct_message.json') as f:
            resp_data = f.read()
        responses.add(
            POST,
            DEFAULT_URL,
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.DestroyDirectMessage(message_id=761517675243679747)

    @responses.activate
    def testShowFriendship(self):
        with open('testdata/get_show_friendship.json') as f:
            resp_data = f.read()
        responses.add(GET, DEFAULT_URL, body=resp_data)

        resp = self.api.ShowFriendship(source_user_id=4012966701, target_user_id=372018022)
        self.assertTrue(resp['relationship']['target'].get('following', None))

        resp = self.api.ShowFriendship(source_screen_name='notinourselves', target_screen_name='__jcbl__')

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.ShowFriendship(source_screen_name='notinourselves')
        )

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.ShowFriendship(target_screen_name='__jcbl__')
        )

    @responses.activate
    def test_UpdateBackgroundImage_deprecation(self):
        responses.add(POST, DEFAULT_URL, body='{}', status=200)
        warnings.simplefilter("always")
        with warnings.catch_warnings(record=True) as w:
            resp = self.api.UpdateBackgroundImage(image='testdata/168NQ.jpg')
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))

    @responses.activate
    @patch('twitter.api.Api.UploadMediaChunked')
    def test_UploadSmallVideoUsesChunkedData(self, mocker):
        responses.add(POST, DEFAULT_URL, body='{}')
        video = NamedTemporaryFile(suffix='.mp4')
        video.write(b'10' * 1024)
        video.seek(0, 0)

        resp = self.api.PostUpdate('test', media=video)
        assert os.path.getsize(video.name) <= 1024 * 1024
        assert isinstance(resp, twitter.Status)
        assert twitter.api.Api.UploadMediaChunked.called
