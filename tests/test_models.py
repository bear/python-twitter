import twitter
import json
import re
import unittest


class ModelsTest(unittest.TestCase):
    with open('testdata/models/models_category.json', 'rb') as f:
        CATEGORY_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_direct_message.json', 'rb') as f:
        DIRECT_MESSAGE_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_direct_message_short.json', 'rb') as f:
        DIRECT_MESSAGE_SHORT_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_hashtag.json', 'rb') as f:
        HASHTAG_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_list.json', 'rb') as f:
        LIST_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_media.json', 'rb') as f:
        MEDIA_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_status.json', 'rb') as f:
        STATUS_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_status_no_user.json', 'rb') as f:
        STATUS_NO_USER_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_trend.json', 'rb') as f:
        TREND_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_url.json', 'rb') as f:
        URL_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_user.json', 'rb') as f:
        USER_SAMPLE_JSON = json.loads(f.read().decode('utf8'))
    with open('testdata/models/models_user_status.json', 'rb') as f:
        USER_STATUS_SAMPLE_JSON = json.loads(f.read().decode('utf8'))

    def test_category(self):
        """ Test twitter.Category object """
        cat = twitter.Category.NewFromJsonDict(self.CATEGORY_SAMPLE_JSON)
        self.assertEqual(cat.__repr__(), "Category(Name=Sports, Slug=sports, Size=26)")
        self.assertTrue(cat.AsJsonString())
        self.assertTrue(cat.AsDict())

    def test_direct_message(self):
        """ Test twitter.DirectMessage object """
        dm = twitter.DirectMessage.NewFromJsonDict(self.DIRECT_MESSAGE_SAMPLE_JSON)
        self.assertEqual(dm.__repr__(), "DirectMessage(ID=678629245946433539, Sender=__jcbl__, Created=Sun Dec 20 17:33:15 +0000 2015, Text='The Communists are distinguished from the other working-class parties by this only: 1. In the national struggles of the proletarians of the [...]')")
        dm_short = twitter.DirectMessage.NewFromJsonDict(self.DIRECT_MESSAGE_SHORT_SAMPLE_JSON)
        self.assertEqual(dm_short.__repr__(), "DirectMessage(ID=678629245946433539, Sender=__jcbl__, Created=Sun Dec 20 17:33:15 +0000 2015, Text='The Communists are distinguished from the other working-class parties by this only')")
        self.assertTrue(dm.AsJsonString())
        self.assertTrue(dm.AsDict())

    def test_hashtag(self):
        """ Test twitter.Hashtag object """
        ht = twitter.Hashtag.NewFromJsonDict(self.HASHTAG_SAMPLE_JSON)
        self.assertEqual(ht.__repr__(), "Hashtag(Text=python)")
        self.assertTrue(ht.AsJsonString())
        self.assertTrue(ht.AsDict())

    def test_list(self):
        """ Test twitter.List object """
        lt = twitter.List.NewFromJsonDict(self.LIST_SAMPLE_JSON)
        self.assertEqual(lt.__repr__(), "List(ID=229581524, FullName=@notinourselves/test, Slug=test, User=notinourselves)")
        self.assertTrue(lt.AsJsonString())
        self.assertTrue(lt.AsDict())

    def test_media(self):
        """ Test twitter.Media object """
        media = twitter.Media.NewFromJsonDict(self.MEDIA_SAMPLE_JSON)
        self.assertEqual(media.__repr__(), "Media(ID=698657676939685888, Type=animated_gif, DisplayURL='pic.twitter.com/NWg4YmiZKA')")
        self.assertTrue(media.AsJsonString())
        self.assertTrue(media.AsDict())

    def test_status(self):
        """ Test twitter.Status object """
        status = twitter.Status.NewFromJsonDict(self.STATUS_SAMPLE_JSON)
        self.assertEqual(status.__repr__(), "Status(ID=698657677329752065, ScreenName='himawari8bot', Created='Sat Feb 13 23:59:05 +0000 2016')")
        self.assertTrue(status.AsJsonString())
        self.assertTrue(status.AsDict())
        self.assertTrue(status.media[0].AsJsonString())
        self.assertTrue(status.media[0].AsDict())
        self.assertTrue(isinstance(status.AsDict()['media'][0], dict))

    def test_status_no_user(self):
        """ Test twitter.Status object which does not contain a 'user' entity. """
        status = twitter.Status.NewFromJsonDict(self.STATUS_NO_USER_SAMPLE_JSON)
        self.assertEqual(status.__repr__(), "Status(ID=698657677329752065, Created='Sat Feb 13 23:59:05 +0000 2016')")
        self.assertTrue(status.AsJsonString())
        self.assertTrue(status.AsDict())

    def test_trend(self):
        """ Test twitter.Trend object """
        trend = twitter.Trend.NewFromJsonDict(self.TREND_SAMPLE_JSON)
        self.assertEqual(trend.__repr__(), "Trend(Name=#ChangeAConsonantSpoilAMovie, Time=None, URL=http:\\/\\/twitter.com\\/search?q=%23ChangeAConsonantSpoilAMovie)")
        self.assertTrue(trend.AsJsonString())
        self.assertTrue(trend.AsDict())

    def test_url(self):
        url = twitter.Url.NewFromJsonDict(self.URL_SAMPLE_JSON)
        self.assertEqual(url.__repr__(), "URL(URL=http://t.co/wtg3XzqQTX, ExpandedURL=http://iseverythingstilltheworst.com)")
        self.assertTrue(url.AsJsonString())
        self.assertTrue(url.AsDict())

    def test_user(self):
        '''Test the twitter.User NewFromJsonDict method'''
        user = twitter.User.NewFromJsonDict(self.USER_SAMPLE_JSON)
        self.assertEqual(user.id, 718443)
        self.assertEqual(user.__repr__(), "User(ID=718443, ScreenName=kesuke)")
        self.assertTrue(user.AsJsonString())
        self.assertTrue(user.AsDict())

    def test_user_status(self):
        """ Test twitter.UserStatus object """
        user_status = twitter.UserStatus.NewFromJsonDict(self.USER_STATUS_SAMPLE_JSON)
        # __repr__ doesn't always order 'connections' in the same manner when
        # call, hence the regex.
        mtch = re.compile(r'UserStatus\(ID=6385432, ScreenName=dickc, Connections=\[[blocking|muting]+, [blocking|muting]+\]\)')
        self.assertTrue(re.findall(mtch, user_status.__repr__()))
        self.assertTrue(user_status.AsJsonString())
        self.assertTrue(user_status.AsDict())
