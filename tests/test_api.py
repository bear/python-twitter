# encoding: utf-8

import os
import time
import urllib
import unittest
import twitter


CONSUMER_KEY = os.getenv('CONSUMER_KEY', None)
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', None)
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY', None)
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET', None)


@unittest.skipIf(not CONSUMER_KEY and not CONSUMER_SECRET, "No tokens provided")
class ApiTest(unittest.TestCase):
    def setUp(self):
        self._urllib = MockUrllib()
        time.sleep(15)
        api = twitter.Api(consumer_key=CONSUMER_SECRET,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=ACCESS_TOKEN_KEY,
                          access_token_secret=ACCESS_TOKEN_SECRET,
                          cache=None)
        api.SetUrllib(self._urllib)
        self._api = api
        print("Testing the API class. This test is time controlled")

    def testTwitterError(self):
        '''Test that twitter responses containing an error message are wrapped.'''
        self._AddHandler('https://api.twitter.com/1.1/statuses/user_timeline.json',
                         curry(self._OpenTestData, 'public_timeline_error.json'))
        # Manually try/catch so we can check the exception's value
        try:
            self._api.GetUserTimeline()
        except twitter.TwitterError as error:
            # If the error message matches, the test passes
            self.assertEqual('test error', error.message)
        else:
            self.fail('TwitterError expected')

    def testGetUserTimeline(self):
        '''Test the twitter.Api GetUserTimeline method'''
        time.sleep(8)
        print('Testing GetUserTimeline')
        self._AddHandler('https://api.twitter.com/1.1/statuses/user_timeline.json?count=1&screen_name=kesuke',
                         curry(self._OpenTestData, 'user_timeline-kesuke.json'))
        statuses = self._api.GetUserTimeline(screen_name='kesuke', count=1)
        # This is rather arbitrary, but spot checking is better than nothing
        self.assertEqual(89512102, statuses[0].id)
        self.assertEqual(718443, statuses[0].user.id)

    # def testGetFriendsTimeline(self):
    #  '''Test the twitter.Api GetFriendsTimeline method'''
    #  self._AddHandler('https://api.twitter.com/1.1/statuses/friends_timeline/kesuke.json',
    #                   curry(self._OpenTestData, 'friends_timeline-kesuke.json'))
    #  statuses = self._api.GetFriendsTimeline('kesuke')
    #  # This is rather arbitrary, but spot checking is better than nothing
    #  self.assertEqual(20, len(statuses))
    #  self.assertEqual(718443, statuses[0].user.id)

    def testGetStatus(self):
        '''Test the twitter.Api GetStatus method'''
        time.sleep(8)
        print('Testing GetStatus')
        self._AddHandler('https://api.twitter.com/1.1/statuses/show.json?include_my_retweet=1&id=89512102',
                         curry(self._OpenTestData, 'show-89512102.json'))
        status = self._api.GetStatus(89512102)
        self.assertEqual(89512102, status.id)
        self.assertEqual(718443, status.user.id)

    def testDestroyStatus(self):
        '''Test the twitter.Api DestroyStatus method'''
        time.sleep(8)
        print('Testing DestroyStatus')
        self._AddHandler('https://api.twitter.com/1.1/statuses/destroy/103208352.json',
                         curry(self._OpenTestData, 'status-destroy.json'))
        status = self._api.DestroyStatus(103208352)
        self.assertEqual(103208352, status.id)

    def testPostUpdate(self):
        '''Test the twitter.Api PostUpdate method'''
        time.sleep(8)
        print('Testing PostUpdate')
        self._AddHandler('https://api.twitter.com/1.1/statuses/update.json',
                         curry(self._OpenTestData, 'update.json'))
        status = self._api.PostUpdate(u'Моё судно на воздушной подушке полно угрей'.encode('utf8'))
        # This is rather arbitrary, but spot checking is better than nothing
        self.assertEqual(u'Моё судно на воздушной подушке полно угрей', status.text)

    def testPostRetweet(self):
        '''Test the twitter.Api PostRetweet method'''
        time.sleep(8)
        print('Testing PostRetweet')
        self._AddHandler('https://api.twitter.com/1.1/statuses/retweet/89512102.json',
                         curry(self._OpenTestData, 'retweet.json'))
        status = self._api.PostRetweet(89512102)
        self.assertEqual(89512102, status.id)

    def testPostUpdateLatLon(self):
        '''Test the twitter.Api PostUpdate method, when used in conjunction with latitude and longitude'''
        time.sleep(8)
        print('Testing PostUpdateLatLon')
        self._AddHandler('https://api.twitter.com/1.1/statuses/update.json',
                         curry(self._OpenTestData, 'update_latlong.json'))
        # test another update with geo parameters, again test somewhat arbitrary
        status = self._api.PostUpdate(u'Моё судно на воздушной подушке полно угрей'.encode('utf8'), latitude=54.2,
                                      longitude=-2)
        self.assertEqual(u'Моё судно на воздушной подушке полно угрей', status.text)
        self.assertEqual(u'Point', status.GetGeo()['type'])
        self.assertEqual(26.2, status.GetGeo()['coordinates'][0])
        self.assertEqual(127.5, status.GetGeo()['coordinates'][1])

    def testGetReplies(self):
        '''Test the twitter.Api GetReplies method'''
        time.sleep(8)
        print('Testing GetReplies')
        self._AddHandler('https://api.twitter.com/1.1/statuses/user_timeline.json',
                         curry(self._OpenTestData, 'replies.json'))
        statuses = self._api.GetReplies()
        self.assertEqual(36657062, statuses[0].id)

    def testGetRetweetsOfMe(self):
        '''Test the twitter.API GetRetweetsOfMe method'''
        time.sleep(8)
        print('Testing GetRetweetsOfMe')
        self._AddHandler('https://api.twitter.com/1.1/statuses/retweets_of_me.json',
                         curry(self._OpenTestData, 'retweets_of_me.json'))
        retweets = self._api.GetRetweetsOfMe()
        self.assertEqual(253650670274637824, retweets[0].id)

    def testGetFriends(self):
        '''Test the twitter.Api GetFriends method'''
        time.sleep(8)
        print('Testing GetFriends')
        self._AddHandler('https://api.twitter.com/1.1/friends/list.json?cursor=123',
                         curry(self._OpenTestData, 'friends.json'))
        users = self._api.GetFriends(cursor=123)
        buzz = [u.status for u in users if u.screen_name == 'buzz']
        self.assertEqual(89543882, buzz[0].id)

    def testGetFollowers(self):
        '''Test the twitter.Api GetFollowers method'''
        time.sleep(8)
        print('Testing GetFollowers')
        self._AddHandler('https://api.twitter.com/1.1/followers/list.json?cursor=-1',
                         curry(self._OpenTestData, 'followers.json'))
        users = self._api.GetFollowers()
        # This is rather arbitrary, but spot checking is better than nothing
        alexkingorg = [u.status for u in users if u.screen_name == 'alexkingorg']
        self.assertEqual(89554432, alexkingorg[0].id)

    # def testGetFeatured(self):
    #  '''Test the twitter.Api GetFeatured method'''
    #  self._AddHandler('https://api.twitter.com/1.1/statuses/featured.json',
    #                   curry(self._OpenTestData, 'featured.json'))
    #  users = self._api.GetFeatured()
    #  # This is rather arbitrary, but spot checking is better than nothing
    #  stevenwright = [u.status for u in users if u.screen_name == 'stevenwright']
    #  self.assertEqual(86991742, stevenwright[0].id)

    def testGetDirectMessages(self):
        '''Test the twitter.Api GetDirectMessages method'''
        time.sleep(8)
        print('Testing GetDirectMessages')
        self._AddHandler('https://api.twitter.com/1.1/direct_messages.json',
                         curry(self._OpenTestData, 'direct_messages.json'))
        statuses = self._api.GetDirectMessages()
        self.assertEqual(u'A légpárnás hajóm tele van angolnákkal.', statuses[0].text)

    def testPostDirectMessage(self):
        '''Test the twitter.Api PostDirectMessage method'''
        time.sleep(8)
        print('Testing PostDirectMessage')
        self._AddHandler('https://api.twitter.com/1.1/direct_messages/new.json',
                         curry(self._OpenTestData, 'direct_messages-new.json'))
        status = self._api.PostDirectMessage('test', u'Моё судно на воздушной подушке полно угрей'.encode('utf8'))
        # This is rather arbitrary, but spot checking is better than nothing
        self.assertEqual(u'Моё судно на воздушной подушке полно угрей', status.text)

    def testDestroyDirectMessage(self):
        '''Test the twitter.Api DestroyDirectMessage method'''
        time.sleep(8)
        print('Testing DestroyDirectMessage')
        self._AddHandler('https://api.twitter.com/1.1/direct_messages/destroy.json',
                         curry(self._OpenTestData, 'direct_message-destroy.json'))
        status = self._api.DestroyDirectMessage(3496342)
        # This is rather arbitrary, but spot checking is better than nothing
        self.assertEqual(673483, status.sender_id)

    def testCreateFriendship(self):
        '''Test the twitter.Api CreateFriendship method'''
        time.sleep(8)
        print('Testing CreateFriendship')
        self._AddHandler('https://api.twitter.com/1.1/friendships/create.json',
                         curry(self._OpenTestData, 'friendship-create.json'))
        user = self._api.CreateFriendship('dewitt')
        # This is rather arbitrary, but spot checking is better than nothing
        self.assertEqual(673483, user.id)

    def testDestroyFriendship(self):
        '''Test the twitter.Api DestroyFriendship method'''
        time.sleep(8)
        print('Testing Destroy Friendship')
        self._AddHandler('https://api.twitter.com/1.1/friendships/destroy.json',
                         curry(self._OpenTestData, 'friendship-destroy.json'))
        user = self._api.DestroyFriendship('dewitt')
        # This is rather arbitrary, but spot checking is better than nothing
        self.assertEqual(673483, user.id)

    def testGetUser(self):
        '''Test the twitter.Api GetUser method'''
        time.sleep(8)
        print('Testing GetUser')
        self._AddHandler('https://api.twitter.com/1.1/users/show.json?user_id=dewitt',
                         curry(self._OpenTestData, 'show-dewitt.json'))
        user = self._api.GetUser('dewitt')
        self.assertEqual('dewitt', user.screen_name)
        self.assertEqual(89586072, user.status.id)

    def _AddHandler(self, url, callback):
        self._urllib.AddHandler(url, callback)

    def _GetTestDataPath(self, filename):
        directory = os.path.dirname(os.path.abspath(__file__))
        test_data_dir = os.path.join(directory, 'testdata')
        return os.path.join(test_data_dir, filename)

    def _OpenTestData(self, filename):
        f = open(self._GetTestDataPath(filename))
        # make sure that the returned object contains an .info() method:
        # headers are set to {}
        return urllib.addinfo(f, {})


class MockUrllib(object):
    '''A mock replacement for urllib that hardcodes specific responses.'''

    def __init__(self):
        self._handlers = {}
        self.HTTPBasicAuthHandler = MockHTTPBasicAuthHandler

    def AddHandler(self, url, callback):
        self._handlers[url] = callback

    def build_opener(self, *handlers):
        return MockOpener(self._handlers)

    def HTTPHandler(self, *args, **kwargs):
        return None

    def HTTPSHandler(self, *args, **kwargs):
        return None

    def OpenerDirector(self):
        return self.build_opener()

    def ProxyHandler(self, *args, **kwargs):
        return None


class MockOpener(object):
    '''A mock opener for urllib'''

    def __init__(self, handlers):
        self._handlers = handlers
        self._opened = False

    def open(self, url, data=None):
        if self._opened:
            raise Exception('MockOpener already opened.')

        # Remove parameters from URL - they're only added by oauth and we
        # don't want to test oauth
        if '?' in url:
            # We split using & and filter on the beginning of each key
            # This is crude but we have to keep the ordering for now
            (url, qs) = url.split('?')

            tokens = [token for token in qs.split('&')
                      if not token.startswith('oauth')]

            if len(tokens) > 0:
                url = "%s?%s" % (url, '&'.join(tokens))

        if url in self._handlers:
            self._opened = True
            return self._handlers[url]()
        else:
            print(url)
            print(self._handlers)

            raise Exception('Unexpected URL %s (Checked: %s)' % (url, self._handlers))

    def add_handler(self, *args, **kwargs):
        pass

    def close(self):
        if not self._opened:
            raise Exception('MockOpener closed before it was opened.')
        self._opened = False


class curry(object):
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52549

    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs
        return self.fun(*(self.pending + args), **kw)


class MockHTTPBasicAuthHandler(object):
    '''A mock replacement for HTTPBasicAuthHandler'''

    def add_password(self, realm, uri, user, passwd):
        # TODO(dewitt): Add verification that the proper args are passed
        pass
