# encoding: utf-8

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

    """ Tests for twitter/api.py """

    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test')
        self.base_url = 'https://api.twitter.com/1.1'
        self._stderr = sys.stderr
        sys.stderr = ErrNull()

    def tearDown(self):
        sys.stderr = self._stderr

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
        with open('testdata/new/get_help_configuration.json') as f:
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
        with open('testdata/new/get_help_configuration.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/help/configuration.json',
            body=resp_data,
            status=200)
        resp = self.api.GetShortUrlLength()
        self.assertEqual(resp, 23)

    @responses.activate
    def testGetSearch(self):
        with open('testdata/search.json') as f:
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
    def testGetSearchGeocode(self):
        with open('testdata/new/get_search_geocode.json') as f:
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

    @responses.activate
    def testGetUsersSearch(self):
        with open('testdata/new/get_users_search.json') as f:
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
        with open('testdata/new/get_trends_current.json') as f:
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
    def testGetUserSuggestionCategories(self):
        with open('testdata/new/get_user_suggestion_categories.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/users/suggestions.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetUserSuggestionCategories()
        self.assertTrue(type(resp[0]) is twitter.Category)

    @responses.activate
    def testGetUserSuggestion(self):
        with open('testdata/new/get_user_suggestion.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/users/suggestions/funny.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        category = twitter.Category(name='Funny', slug='funny', size=20)
        resp = self.api.GetUserSuggestion(category=category)
        self.assertTrue(type(resp[0]) is twitter.User)

    @responses.activate
    def testGetHomeTimeline(self):
        with open('testdata/new/get_home_timeline.json') as f:
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
        with open('testdata/new/get_user_timeline.json') as f:
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
    def testGetStatus(self):
        with open('testdata/new/get_status.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/show.json?include_my_retweet=1&id=397',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetStatus(status_id=397)

        self.assertTrue(type(resp) is twitter.Status)
        self.assertEqual(resp.id, 397)
        self.assertEqual(resp.user.id, 12)

        self.assertEqual(resp.CreatedAtInSeconds, 1143400628)
        self.assertFalse(resp != resp)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetStatus(status_id='test'))

    @responses.activate
    def testGetStatusExtraParams(self):
        with open('testdata/new/get_status_extra_params.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/show.json?include_my_retweet=1&id=397&trim_user=1&include_entities=none',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetStatus(status_id=397, trim_user=True, include_entities=False)
        self.assertFalse(resp.user.screen_name)


    @responses.activate
    def testGetStatusOembed(self):
        with open('testdata/new/get_status_oembed.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/oembed.json?id=397',
            body=resp_data,
            match_querystring=True,
            status=200)
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/oembed.json?url=https://twitter.com/jack/statuses/397',
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
    def testGetRetweets(self):
        with open('testdata/new/get_retweets.json') as f:
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
        with open('testdata/new/get_retweeters.json') as f:
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
        with open('testdata/new/get_blocks.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/list.json?cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetBlocks()
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0].screen_name, 'RedScareBot')

    @responses.activate
    def testGetFriends(self):
        with open('testdata/new/get_friends.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friends/list.json?cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetFriends()
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0].screen_name, '__jcbl__')

    @responses.activate
    def testGetFriendIDs(self):
        with open('testdata/new/get_friends_ids.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friends/ids.json?cursor=-1&count=5000',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetFriendIDs()
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is int)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], 372018022)

    @responses.activate
    def testGetFollowerIDs(self):
        with open('testdata/new/get_follower_ids_paged.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/friends/ids.json?cursor=-1&count=5000',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetFriendIDs()
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is int)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], 372018022)

    @responses.activate
    def testUsersLookup(self):
        with open('testdata/new/users_lookup.json') as f:
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
        with open('testdata/new/get_user.json') as f:
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
        with open('testdata/new/get_direct_messages.json') as f:
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
        with open('testdata/new/get_sent_direct_messages.json') as f:
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
        with open('testdata/new/get_favorites.json') as f:
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
        with open('testdata/new/get_mentions.json') as f:
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
    def testGetMemberships(self):
        with open('testdata/new/get_memberships.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/memberships.json?filter_to_owned_lists=False&cursor=-1&count=20',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetMemberships()
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(lst) is twitter.List for lst in resp])
        self.assertEqual(resp[0].id, 210635540)

    @responses.activate
    def testGetListsList(self):
        with open('testdata/new/get_lists_list.json') as f:
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

        with open('testdata/new/get_lists_list_screen_name.json') as f:
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

        with open('testdata/new/get_lists_list_user_id.json') as f:
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
    def testGetListTimeline(self):
        with open('testdata/new/get_list_timeline.json') as f:
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
    def testGetListMembers(self):
        with open('testdata/new/get_list_members.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/members.json?cursor=-1&list_id=189643778',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListMembers(list_id=189643778)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(resp[0].id, 4040207472)

    @responses.activate
    def testGetLists(self):
        with open('testdata/new/get_lists.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/ownerships.json?cursor=-1',
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
