import twitter
import json
import unittest


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
        twitter.User(id=673483,
                     name='DeWitt',
                     screen_name='dewitt',
                     description=u'Indeterminate things',
                     url='https://twitter.com/dewitt',
                     profile_image_url='https://twitter.com/system/user/profile_image/673483/normal/me.jpg',
                     status=self._GetSampleStatus())

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
        user.profile_image_url = 'https://twitter.com/system/user/profile_image/673483/normal/me.jpg'
        self.assertEqual('https://twitter.com/system/user/profile_image/673483/normal/me.jpg', user.profile_image_url)
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

    def testHash(self):
        '''Test the twitter.User __hash__ method'''
        user = self._GetSampleUser()
        self.assertEqual(hash(user), hash(user.id))

    def testNewFromJsonDict(self):
        '''Test the twitter.User NewFromJsonDict method'''
        data = json.loads(UserTest.SAMPLE_JSON)
        user = twitter.User.NewFromJsonDict(data)
        self.assertEqual(self._GetSampleUser(), user)
