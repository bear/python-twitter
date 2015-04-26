# encoding: utf-8

import twitter
import calendar
import time
import json
import unittest


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

    def testProperties(self):
        '''Test all of the twitter.Status properties'''
        status = twitter.Status()
        status.id = 1
        self.assertEqual(1, status.id)
        created_at = calendar.timegm((2007, 1, 26, 23, 17, 14, -1, -1, -1))
        status.created_at = 'Fri Jan 26 23:17:14 +0000 2007'
        self.assertEqual('Fri Jan 26 23:17:14 +0000 2007', status.created_at)
        self.assertEqual(created_at, status.CreatedAtInSeconds)
        status.now = created_at + 10
        self.assertEqual('about 10 seconds ago', status.RelativeCreatedAt)
        status.user = self._GetSampleUser()
        self.assertEqual(718443, status.user.id)

    def _ParseDate(self, string):
        return calendar.timegm(time.strptime(string, '%b %d %H:%M:%S %Y'))

    def testRelativeCreatedAt(self):
        '''Test various permutations of Status RelativeCreatedAt'''
        status = twitter.Status(created_at='Fri Jan 01 12:00:00 +0000 2007')
        status.now = self._ParseDate('Jan 01 12:00:00 2007')
        self.assertEqual('about a second ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:00:01 2007')
        self.assertEqual('about a second ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:00:02 2007')
        self.assertEqual('about 2 seconds ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:00:05 2007')
        self.assertEqual('about 5 seconds ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:00:50 2007')
        self.assertEqual('about a minute ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:01:00 2007')
        self.assertEqual('about a minute ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:01:10 2007')
        self.assertEqual('about a minute ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:02:00 2007')
        self.assertEqual('about 2 minutes ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:31:50 2007')
        self.assertEqual('about 31 minutes ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 12:50:00 2007')
        self.assertEqual('about an hour ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 13:00:00 2007')
        self.assertEqual('about an hour ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 13:10:00 2007')
        self.assertEqual('about an hour ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 14:00:00 2007')
        self.assertEqual('about 2 hours ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 01 19:00:00 2007')
        self.assertEqual('about 7 hours ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 02 11:30:00 2007')
        self.assertEqual('about a day ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Jan 04 12:00:00 2007')
        self.assertEqual('about 3 days ago', status.RelativeCreatedAt)
        status.now = self._ParseDate('Feb 04 12:00:00 2007')
        self.assertEqual('about 34 days ago', status.RelativeCreatedAt)

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
        data = json.loads(StatusTest.SAMPLE_JSON)
        status = twitter.Status.NewFromJsonDict(data)
        self.assertEqual(self._GetSampleStatus(), status)
