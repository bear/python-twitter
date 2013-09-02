#!/usr/bin/env python
# -*- coding: utf-8 -*-#
# vim: sw=2 ts=2 sts=2
#
# Copyright 2007 The Python-Twitter Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Unit tests for the twitter.py library'''

__author__ = 'python-twitter@googlegroups.com'

import os
import simplejson
import time
import calendar
import unittest
import urllib

import twitter

class StatusTest(unittest.TestCase):

  SAMPLE_JSON = '''{"created_at": "Fri Jan 26 23:17:14 +0000 2007", "id": 4391023, "text": "A l\u00e9gp\u00e1rn\u00e1s haj\u00f3m tele van angoln\u00e1kkal.", "user": {"description": "Canvas. JC Penny. Three ninety-eight.", "id": 718443, "location": "Okinawa, Japan", "name": "Kesuke Miyagi", "profile_image_url": "https://twitter.com/system/user/profile_image/718443/normal/kesuke.png", "screen_name": "kesuke", "url": "https://twitter.com/kesuke"}}'''

  def _GetSampleUser(self):
    return twitter.User(id=718443,
                        name='Kesuke Miyagi',
                        screen_name='kesuke',
                        description=u'Canvas. JC Penny. Three ninety-eight.',
                        location='Okinawa, Japan',
                        url='https://twitter.com/kesuke',
                        profile_image_url='https://twitter.com/system/user/pro'
                                          'file_image/718443/normal/kesuke.pn'
                                          'g')

  def _GetSampleStatus(self):
    return twitter.Status(created_at='Fri Jan 26 23:17:14 +0000 2007',
                          id=4391023,
                          text=u'A légpárnás hajóm tele van angolnákkal.',
                          user=self._GetSampleUser())

  def testInit(self):
    '''Test the twitter.Status constructor'''
    status = twitter.Status(created_at='Fri Jan 26 23:17:14 +0000 2007',
                            id=4391023,
                            text=u'A légpárnás hajóm tele van angolnákkal.',
                            user=self._GetSampleUser())

  def testGettersAndSetters(self):
    '''Test all of the twitter.Status getters and setters'''
    status = twitter.Status()
    status.SetId(4391023)
    self.assertEqual(4391023, status.GetId())
    created_at = calendar.timegm((2007, 1, 26, 23, 17, 14, -1, -1, -1))
    status.SetCreatedAt('Fri Jan 26 23:17:14 +0000 2007')
    self.assertEqual('Fri Jan 26 23:17:14 +0000 2007', status.GetCreatedAt())
    self.assertEqual(created_at, status.GetCreatedAtInSeconds())
    status.SetNow(created_at + 10)
    self.assertEqual("about 10 seconds ago", status.GetRelativeCreatedAt())
    status.SetText(u'A légpárnás hajóm tele van angolnákkal.')
    self.assertEqual(u'A légpárnás hajóm tele van angolnákkal.',
                     status.GetText())
    status.SetUser(self._GetSampleUser())
    self.assertEqual(718443, status.GetUser().id)

  def testProperties(self):
    '''Test all of the twitter.Status properties'''
    status = twitter.Status()
    status.id = 1
    self.assertEqual(1, status.id)
    created_at = calendar.timegm((2007, 1, 26, 23, 17, 14, -1, -1, -1))
    status.created_at = 'Fri Jan 26 23:17:14 +0000 2007'
    self.assertEqual('Fri Jan 26 23:17:14 +0000 2007', status.created_at)
    self.assertEqual(created_at, status.created_at_in_seconds)
    status.now = created_at + 10
    self.assertEqual('about 10 seconds ago', status.relative_created_at)
    status.user = self._GetSampleUser()
    self.assertEqual(718443, status.user.id)

  def _ParseDate(self, string):
    return calendar.timegm(time.strptime(string, '%b %d %H:%M:%S %Y'))

  def testRelativeCreatedAt(self):
    '''Test various permutations of Status relative_created_at'''
    status = twitter.Status(created_at='Fri Jan 01 12:00:00 +0000 2007')
    status.now = self._ParseDate('Jan 01 12:00:00 2007')
    self.assertEqual('about a second ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:00:01 2007')
    self.assertEqual('about a second ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:00:02 2007')
    self.assertEqual('about 2 seconds ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:00:05 2007')
    self.assertEqual('about 5 seconds ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:00:50 2007')
    self.assertEqual('about a minute ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:01:00 2007')
    self.assertEqual('about a minute ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:01:10 2007')
    self.assertEqual('about a minute ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:02:00 2007')
    self.assertEqual('about 2 minutes ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:31:50 2007')
    self.assertEqual('about 31 minutes ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 12:50:00 2007')
    self.assertEqual('about an hour ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 13:00:00 2007')
    self.assertEqual('about an hour ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 13:10:00 2007')
    self.assertEqual('about an hour ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 14:00:00 2007')
    self.assertEqual('about 2 hours ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 01 19:00:00 2007')
    self.assertEqual('about 7 hours ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 02 11:30:00 2007')
    self.assertEqual('about a day ago', status.relative_created_at)
    status.now = self._ParseDate('Jan 04 12:00:00 2007')
    self.assertEqual('about 3 days ago', status.relative_created_at)
    status.now = self._ParseDate('Feb 04 12:00:00 2007')
    self.assertEqual('about 34 days ago', status.relative_created_at)

  def testAsJsonString(self):
    '''Test the twitter.Status AsJsonString method'''
    self.assertEqual(StatusTest.SAMPLE_JSON,
                     self._GetSampleStatus().AsJsonString())

  def testAsDict(self):
    '''Test the twitter.Status AsDict method'''
    status = self._GetSampleStatus()
    data = status.AsDict()
    self.assertEqual(4391023, data['id'])
    self.assertEqual('Fri Jan 26 23:17:14 +0000 2007', data['created_at'])
    self.assertEqual(u'A légpárnás hajóm tele van angolnákkal.', data['text'])
    self.assertEqual(718443, data['user']['id'])

  def testEq(self):
    '''Test the twitter.Status __eq__ method'''
    status = twitter.Status()
    status.created_at = 'Fri Jan 26 23:17:14 +0000 2007'
    status.id = 4391023
    status.text = u'A légpárnás hajóm tele van angolnákkal.'
    status.user = self._GetSampleUser()
    self.assertEqual(status, self._GetSampleStatus())

  def testNewFromJsonDict(self):
    '''Test the twitter.Status NewFromJsonDict method'''
    data = simplejson.loads(StatusTest.SAMPLE_JSON)
    status = twitter.Status.NewFromJsonDict(data)
    self.assertEqual(self._GetSampleStatus(), status)

class UserTest(unittest.TestCase):

  SAMPLE_JSON = '''{"description": "Indeterminate things", "id": 673483, "location": "San Francisco, CA", "name": "DeWitt", "profile_image_url": "https://twitter.com/system/user/profile_image/673483/normal/me.jpg", "screen_name": "dewitt", "status": {"created_at": "Fri Jan 26 17:28:19 +0000 2007", "id": 4212713, "text": "\\"Select all\\" and archive your Gmail inbox.  The page loads so much faster!"}, "url": "http://unto.net/"}'''

  def _GetSampleStatus(self):
    return twitter.Status(created_at='Fri Jan 26 17:28:19 +0000 2007',
                          id=4212713,
                          text='"Select all" and archive your Gmail inbox. '
                               ' The page loads so much faster!')

  def _GetSampleUser(self):
    return twitter.User(id=673483,
                        name='DeWitt',
                        screen_name='dewitt',
                        description=u'Indeterminate things',
                        location='San Francisco, CA',
                        url='http://unto.net/',
                        profile_image_url='https://twitter.com/system/user/prof'
                                          'ile_image/673483/normal/me.jpg',
                        status=self._GetSampleStatus())



  def testInit(self):
    '''Test the twitter.User constructor'''
    user = twitter.User(id=673483,
                        name='DeWitt',
                        screen_name='dewitt',
                        description=u'Indeterminate things',
                        url='https://twitter.com/dewitt',
                        profile_image_url='https://twitter.com/system/user/prof'
                                          'ile_image/673483/normal/me.jpg',
                        status=self._GetSampleStatus())

  def testGettersAndSetters(self):
    '''Test all of the twitter.User getters and setters'''
    user = twitter.User()
    user.SetId(673483)
    self.assertEqual(673483, user.GetId())
    user.SetName('DeWitt')
    self.assertEqual('DeWitt', user.GetName())
    user.SetScreenName('dewitt')
    self.assertEqual('dewitt', user.GetScreenName())
    user.SetDescription('Indeterminate things')
    self.assertEqual('Indeterminate things', user.GetDescription())
    user.SetLocation('San Francisco, CA')
    self.assertEqual('San Francisco, CA', user.GetLocation())
    user.SetProfileImageUrl('https://twitter.com/system/user/profile_im'
                            'age/673483/normal/me.jpg')
    self.assertEqual('https://twitter.com/system/user/profile_image/673'
                     '483/normal/me.jpg', user.GetProfileImageUrl())
    user.SetStatus(self._GetSampleStatus())
    self.assertEqual(4212713, user.GetStatus().id)

  def testProperties(self):
    '''Test all of the twitter.User properties'''
    user = twitter.User()
    user.id = 673483
    self.assertEqual(673483, user.id)
    user.name = 'DeWitt'
    self.assertEqual('DeWitt', user.name)
    user.screen_name = 'dewitt'
    self.assertEqual('dewitt', user.screen_name)
    user.description = 'Indeterminate things'
    self.assertEqual('Indeterminate things', user.description)
    user.location = 'San Francisco, CA'
    self.assertEqual('San Francisco, CA', user.location)
    user.profile_image_url = 'https://twitter.com/system/user/profile_i' \
                             'mage/673483/normal/me.jpg'
    self.assertEqual('https://twitter.com/system/user/profile_image/6734'
                     '83/normal/me.jpg', user.profile_image_url)
    self.status = self._GetSampleStatus()
    self.assertEqual(4212713, self.status.id)

  def testAsJsonString(self):
    '''Test the twitter.User AsJsonString method'''
    self.assertEqual(UserTest.SAMPLE_JSON,
                     self._GetSampleUser().AsJsonString())

  def testAsDict(self):
    '''Test the twitter.User AsDict method'''
    user = self._GetSampleUser()
    data = user.AsDict()
    self.assertEqual(673483, data['id'])
    self.assertEqual('DeWitt', data['name'])
    self.assertEqual('dewitt', data['screen_name'])
    self.assertEqual('Indeterminate things', data['description'])
    self.assertEqual('San Francisco, CA', data['location'])
    self.assertEqual('https://twitter.com/system/user/profile_image/6734'
                     '83/normal/me.jpg', data['profile_image_url'])
    self.assertEqual('http://unto.net/', data['url'])
    self.assertEqual(4212713, data['status']['id'])

  def testEq(self):
    '''Test the twitter.User __eq__ method'''
    user = twitter.User()
    user.id = 673483
    user.name = 'DeWitt'
    user.screen_name = 'dewitt'
    user.description = 'Indeterminate things'
    user.location = 'San Francisco, CA'
    user.profile_image_url = 'https://twitter.com/system/user/profile_image/67' \
                             '3483/normal/me.jpg'
    user.url = 'http://unto.net/'
    user.status = self._GetSampleStatus()
    self.assertEqual(user, self._GetSampleUser())

  def testNewFromJsonDict(self):
    '''Test the twitter.User NewFromJsonDict method'''
    data = simplejson.loads(UserTest.SAMPLE_JSON)
    user = twitter.User.NewFromJsonDict(data)
    self.assertEqual(self._GetSampleUser(), user)

class TrendTest(unittest.TestCase):

  SAMPLE_JSON = '''{"name": "Kesuke Miyagi", "query": "Kesuke Miyagi"}'''

  def _GetSampleTrend(self):
    return twitter.Trend(name='Kesuke Miyagi',
                         query='Kesuke Miyagi',
                         timestamp='Fri Jan 26 23:17:14 +0000 2007')

  def testInit(self):
    '''Test the twitter.Trend constructor'''
    trend = twitter.Trend(name='Kesuke Miyagi',
                          query='Kesuke Miyagi',
                          timestamp='Fri Jan 26 23:17:14 +0000 2007')

  def testProperties(self):
    '''Test all of the twitter.Trend properties'''
    trend = twitter.Trend()
    trend.name = 'Kesuke Miyagi'
    self.assertEqual('Kesuke Miyagi', trend.name)
    trend.query = 'Kesuke Miyagi'
    self.assertEqual('Kesuke Miyagi', trend.query)
    trend.timestamp = 'Fri Jan 26 23:17:14 +0000 2007'
    self.assertEqual('Fri Jan 26 23:17:14 +0000 2007', trend.timestamp)

  def testNewFromJsonDict(self):
    '''Test the twitter.Trend NewFromJsonDict method'''
    data = simplejson.loads(TrendTest.SAMPLE_JSON)
    trend = twitter.Trend.NewFromJsonDict(data, timestamp='Fri Jan 26 23:17:14 +0000 2007')
    self.assertEqual(self._GetSampleTrend(), trend)

  def testEq(self):
    '''Test the twitter.Trend __eq__ method'''
    trend = twitter.Trend()
    trend.name = 'Kesuke Miyagi'
    trend.query = 'Kesuke Miyagi'
    trend.timestamp = 'Fri Jan 26 23:17:14 +0000 2007'
    self.assertEqual(trend, self._GetSampleTrend())

class FileCacheTest(unittest.TestCase):

  def testInit(self):
    """Test the twitter._FileCache constructor"""
    cache = twitter._FileCache()
    self.assert_(cache is not None, 'cache is None')

  def testSet(self):
    """Test the twitter._FileCache.Set method"""
    cache = twitter._FileCache()
    cache.Set("foo",'Hello World!')
    cache.Remove("foo")

  def testRemove(self):
    """Test the twitter._FileCache.Remove method"""
    cache = twitter._FileCache()
    cache.Set("foo",'Hello World!')
    cache.Remove("foo")
    data = cache.Get("foo")
    self.assertEqual(data, None, 'data is not None')

  def testGet(self):
    """Test the twitter._FileCache.Get method"""
    cache = twitter._FileCache()
    cache.Set("foo",'Hello World!')
    data = cache.Get("foo")
    self.assertEqual('Hello World!', data)
    cache.Remove("foo")

  def testGetCachedTime(self):
    """Test the twitter._FileCache.GetCachedTime method"""
    now = time.time()
    cache = twitter._FileCache()
    cache.Set("foo",'Hello World!')
    cached_time = cache.GetCachedTime("foo")
    delta = cached_time - now
    self.assert_(delta <= 1,
                 'Cached time differs from clock time by more than 1 second.')
    cache.Remove("foo")

class ApiTest(unittest.TestCase):

  def setUp(self):
    self._urllib = MockUrllib()
    time.sleep(15)
    api = twitter.Api(consumer_key='yDkaORxEcwX6SheX6pa1fw',
                      consumer_secret='VYIGd2KITohR4ygmHrcyZgV0B74CXi5wsT1eryVtw',
                      access_token_key='227846642-8IjK2K32CDFt3682SNOOpnzegAja3TyVpzFOGrQj',
                      access_token_secret='L6of20EZdBv48EA2GE8Js6roIfZFnCKBpoPwvBDxF8',
                      cache=None)
    api.SetUrllib(self._urllib)
    self._api = api
    print "Testing the API class. This test is time controled"

  def testTwitterError(self):
    '''Test that twitter responses containing an error message are wrapped.'''
    self._AddHandler('https://api.twitter.com/1.1/statuses/user_timeline.json',
                     curry(self._OpenTestData, 'public_timeline_error.json'))
    # Manually try/catch so we can check the exception's value
    try:
      statuses = self._api.GetUserTimeline()
    except twitter.TwitterError, error:
      # If the error message matches, the test passes
      self.assertEqual('test error', error.message)
    else:
      self.fail('TwitterError expected')

  def testGetUserTimeline(self):
    '''Test the twitter.Api GetUserTimeline method'''
    time.sleep(8)
    print 'Testing GetUserTimeline'
    self._AddHandler('https://api.twitter.com/1.1/statuses/user_timeline.json?count=1&screen_name=kesuke',
                     curry(self._OpenTestData, 'user_timeline-kesuke.json'))
    statuses = self._api.GetUserTimeline(screen_name='kesuke', count=1)
    # This is rather arbitrary, but spot checking is better than nothing
    self.assertEqual(89512102, statuses[0].id)
    self.assertEqual(718443, statuses[0].user.id)

  #def testGetFriendsTimeline(self):
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
    print 'Testing GetStatus'
    self._AddHandler('https://api.twitter.com/1.1/statuses/show.json?include_my_retweet=1&id=89512102',
                     curry(self._OpenTestData, 'show-89512102.json'))
    status = self._api.GetStatus(89512102)
    self.assertEqual(89512102, status.id)
    self.assertEqual(718443, status.user.id)

  def testDestroyStatus(self):
    '''Test the twitter.Api DestroyStatus method'''
    time.sleep(8)
    print 'Testing DestroyStatus'
    self._AddHandler('https://api.twitter.com/1.1/statuses/destroy/103208352.json',
                     curry(self._OpenTestData, 'status-destroy.json'))
    status = self._api.DestroyStatus(103208352)
    self.assertEqual(103208352, status.id)

  def testPostUpdate(self):
    '''Test the twitter.Api PostUpdate method'''
    time.sleep(8)
    print 'Testing PostUpdate'
    self._AddHandler('https://api.twitter.com/1.1/statuses/update.json',
                     curry(self._OpenTestData, 'update.json'))
    status = self._api.PostUpdate(u'Моё судно на воздушной подушке полно угрей'.encode('utf8'))
    # This is rather arbitrary, but spot checking is better than nothing
    self.assertEqual(u'Моё судно на воздушной подушке полно угрей', status.text)

  def testPostRetweet(self):
    '''Test the twitter.Api PostRetweet method'''
    time.sleep(8)
    print 'Testing PostRetweet'
    self._AddHandler('https://api.twitter.com/1.1/statuses/retweet/89512102.json',
                     curry(self._OpenTestData, 'retweet.json'))
    status = self._api.PostRetweet(89512102)
    self.assertEqual(89512102, status.id)

  def testPostUpdateLatLon(self):
    '''Test the twitter.Api PostUpdate method, when used in conjunction with latitude and longitude'''
    time.sleep(8)
    print 'Testing PostUpdateLatLon'
    self._AddHandler('https://api.twitter.com/1.1/statuses/update.json',
                     curry(self._OpenTestData, 'update_latlong.json'))
    #test another update with geo parameters, again test somewhat arbitrary
    status = self._api.PostUpdate(u'Моё судно на воздушной подушке полно угрей'.encode('utf8'), latitude=54.2, longitude=-2)
    self.assertEqual(u'Моё судно на воздушной подушке полно угрей', status.text)
    self.assertEqual(u'Point',status.GetGeo()['type'])
    self.assertEqual(26.2,status.GetGeo()['coordinates'][0])
    self.assertEqual(127.5,status.GetGeo()['coordinates'][1])

  def testGetReplies(self):
    '''Test the twitter.Api GetReplies method'''
    time.sleep(8)
    print 'Testing GetReplies'
    self._AddHandler('https://api.twitter.com/1.1/statuses/user_timeline.json',
                     curry(self._OpenTestData, 'replies.json'))
    statuses = self._api.GetReplies()
    self.assertEqual(36657062, statuses[0].id)

  def testGetRetweetsOfMe(self):
    '''Test the twitter.API GetRetweetsOfMe method'''
    time.sleep(8)
    print 'Testing GetRetweetsOfMe'
    self._AddHandler('https://api.twitter.com/1.1/statuses/retweets_of_me.json',
        curry(self._OpenTestData, 'retweets_of_me.json'))
    retweets = self._api.GetRetweetsOfMe()
    self.assertEqual(253650670274637824, retweets[0].id)

  def testGetFriends(self):
    '''Test the twitter.Api GetFriends method'''
    time.sleep(8)
    print 'Testing GetFriends'
    self._AddHandler('https://api.twitter.com/1.1/friends/list.json?cursor=123',
                     curry(self._OpenTestData, 'friends.json'))
    users = self._api.GetFriends(cursor=123)
    buzz = [u.status for u in users if u.screen_name == 'buzz']
    self.assertEqual(89543882, buzz[0].id)

  def testGetFollowers(self):
    '''Test the twitter.Api GetFollowers method'''
    time.sleep(8)
    print 'Testing GetFollowers'
    self._AddHandler('https://api.twitter.com/1.1/followers/list.json?cursor=-1',
                     curry(self._OpenTestData, 'followers.json'))
    users = self._api.GetFollowers()
    # This is rather arbitrary, but spot checking is better than nothing
    alexkingorg = [u.status for u in users if u.screen_name == 'alexkingorg']
    self.assertEqual(89554432, alexkingorg[0].id)

  #def testGetFeatured(self):
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
    print 'Testing GetDirectMessages'
    self._AddHandler('https://api.twitter.com/1.1/direct_messages.json',
                     curry(self._OpenTestData, 'direct_messages.json'))
    statuses = self._api.GetDirectMessages()
    self.assertEqual(u'A légpárnás hajóm tele van angolnákkal.', statuses[0].text)

  def testPostDirectMessage(self):
    '''Test the twitter.Api PostDirectMessage method'''
    time.sleep(8)
    print 'Testing PostDirectMessage'
    self._AddHandler('https://api.twitter.com/1.1/direct_messages/new.json',
                     curry(self._OpenTestData, 'direct_messages-new.json'))
    status = self._api.PostDirectMessage('test', u'Моё судно на воздушной подушке полно угрей'.encode('utf8'))
    # This is rather arbitrary, but spot checking is better than nothing
    self.assertEqual(u'Моё судно на воздушной подушке полно угрей', status.text)

  def testDestroyDirectMessage(self):
    '''Test the twitter.Api DestroyDirectMessage method'''
    time.sleep(8)
    print 'Testing DestroyDirectMessage'
    self._AddHandler('https://api.twitter.com/1.1/direct_messages/destroy.json',
                     curry(self._OpenTestData, 'direct_message-destroy.json'))
    status = self._api.DestroyDirectMessage(3496342)
    # This is rather arbitrary, but spot checking is better than nothing
    self.assertEqual(673483, status.sender_id)

  def testCreateFriendship(self):
    '''Test the twitter.Api CreateFriendship method'''
    time.sleep(8)
    print 'Testing CreateFriendship'
    self._AddHandler('https://api.twitter.com/1.1/friendships/create.json',
                     curry(self._OpenTestData, 'friendship-create.json'))
    user = self._api.CreateFriendship('dewitt')
    # This is rather arbitrary, but spot checking is better than nothing
    self.assertEqual(673483, user.id)

  def testDestroyFriendship(self):
    '''Test the twitter.Api DestroyFriendship method'''
    time.sleep(8)
    print 'Testing Destroy Friendship'
    self._AddHandler('https://api.twitter.com/1.1/friendships/destroy.json',
                     curry(self._OpenTestData, 'friendship-destroy.json'))
    user = self._api.DestroyFriendship('dewitt')
    # This is rather arbitrary, but spot checking is better than nothing
    self.assertEqual(673483, user.id)

  def testGetUser(self):
    '''Test the twitter.Api GetUser method'''
    time.sleep(8)
    print 'Testing GetUser'
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

  def ProxyHandler(self,*args,**kwargs):
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
            url = "%s?%s"%(url, '&'.join(tokens))

    if url in self._handlers:
      self._opened = True
      return self._handlers[url]()
    else:
      print url
      print self._handlers

      raise Exception('Unexpected URL %s (Checked: %s)' % (url, self._handlers))

  def add_handler(self, *args, **kwargs):
      pass

  def close(self):
    if not self._opened:
      raise Exception('MockOpener closed before it was opened.')
    self._opened = False

class ParseTest(unittest.TestCase):
  """ Test the ParseTweet class """
  
  def testParseTweets(self):    
    handles4 =  u"""Do not use this word! Hurting me! @raja7727: @qadirbasha @manion @Jayks3 உடன்பிறப்பு”""";
    
    data = twitter.ParseTweet("@twitter",handles4)
    self.assertEqual([data.RT,data.MT,len(data.UserHandles)],[False,False,4])
    
    hashtag_n_URL = u"மனதிற்கு மிகவும் நெருக்கமான பாடல்! உயிரையே கொடுக்கலாம் சார்! #KeladiKanmani https://www.youtube.com/watch?v=FHTiG_g2fM4 … #HBdayRajaSir";
    
    data = twitter.ParseTweet("@twitter",hashtag_n_URL)
    self.assertEqual([len(data.Hashtags),len(data.URLs)],[2,1])
    
    url_only = u"""The #Rainbow #Nebula, 544,667 #lightyears away. pic.twitter.com/2A4wSUK25A""";
    data = twitter.ParseTweet("@twitter",url_only)
    self.assertEqual([data.MT,len(data.Hashtags),len(data.URLs)],[False,3,1])
    
    url_handle = u"""RT ‏@BarackObama POTUS recommends Python-Twitter #unrelated picture pic.twitter.com/w8lFIfuUmI""";
    data = twitter.ParseTweet("@twitter",url_handle)
    self.assertEqual([data.RT,len(data.Hashtags),len(data.URLs),len(data.UserHandles)],[True,1,1,1])
    
class MockHTTPBasicAuthHandler(object):
  '''A mock replacement for HTTPBasicAuthHandler'''

  def add_password(self, realm, uri, user, passwd):
    # TODO(dewitt): Add verification that the proper args are passed
    pass

class curry:
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


def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(FileCacheTest))
  suite.addTests(unittest.makeSuite(StatusTest))
  suite.addTests(unittest.makeSuite(UserTest))
  suite.addTests(unittest.makeSuite(ApiTest))
  suite.addTests(unittest.makeSuite(ParseTest))
  return suite

if __name__ == '__main__':
  unittest.main()
