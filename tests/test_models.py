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
        try:
            cat.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(cat.AsJsonString())
        self.assertTrue(cat.AsDict())

    def test_direct_message(self):
        """ Test twitter.DirectMessage object """
        dm = twitter.DirectMessage.NewFromJsonDict(self.DIRECT_MESSAGE_SAMPLE_JSON)
        dm_short = twitter.DirectMessage.NewFromJsonDict(self.DIRECT_MESSAGE_SHORT_SAMPLE_JSON)
        try:
            dm.__repr__()
            dm_short.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(dm.AsJsonString())
        self.assertTrue(dm.AsDict())

    def test_direct_message_sender_is_user_model(self):
        """Test that each Direct Message object contains a fully hydrated
        twitter.models.User object for both ``dm.sender`` & ``dm.recipient``."""
        dm = twitter.DirectMessage.NewFromJsonDict(self.DIRECT_MESSAGE_SAMPLE_JSON)

        self.assertTrue(isinstance(dm.sender, twitter.models.User))
        self.assertEqual(dm.sender.id, 372018022)

        # Let's make sure this doesn't break the construction of the DM object.
        self.assertEqual(dm.id, 678629245946433539)

    def test_direct_message_recipient_is_user_model(self):
        """Test that each Direct Message object contains a fully hydrated
        twitter.models.User object for both ``dm.sender`` & ``dm.recipient``."""
        dm = twitter.DirectMessage.NewFromJsonDict(self.DIRECT_MESSAGE_SAMPLE_JSON)

        self.assertTrue(isinstance(dm.recipient, twitter.models.User))
        self.assertEqual(dm.recipient.id, 4012966701)

        # Same as above.
        self.assertEqual(dm.id, 678629245946433539)

    def test_hashtag(self):
        """ Test twitter.Hashtag object """
        ht = twitter.Hashtag.NewFromJsonDict(self.HASHTAG_SAMPLE_JSON)
        try:
            ht.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(ht.AsJsonString())
        self.assertTrue(ht.AsDict())

    def test_list(self):
        """ Test twitter.List object """
        lt = twitter.List.NewFromJsonDict(self.LIST_SAMPLE_JSON)
        try:
            lt.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(lt.AsJsonString())
        self.assertTrue(lt.AsDict())

    def test_media(self):
        """ Test twitter.Media object """
        media = twitter.Media.NewFromJsonDict(self.MEDIA_SAMPLE_JSON)
        try:
            media.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(media.AsJsonString())
        self.assertTrue(media.AsDict())

    def test_status(self):
        """ Test twitter.Status object """
        status = twitter.Status.NewFromJsonDict(self.STATUS_SAMPLE_JSON)
        try:
            status.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(status.AsJsonString())
        self.assertTrue(status.AsDict())
        self.assertTrue(status.media[0].AsJsonString())
        self.assertTrue(status.media[0].AsDict())
        self.assertTrue(isinstance(status.AsDict()['media'][0], dict))
        self.assertEqual(status.id_str, "698657677329752065")
        self.assertTrue(isinstance(status.user, twitter.User))

    def test_status_no_user(self):
        """ Test twitter.Status object which does not contain a 'user' entity. """
        status = twitter.Status.NewFromJsonDict(self.STATUS_NO_USER_SAMPLE_JSON)
        try:
            status.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(status.AsJsonString())
        self.assertTrue(status.AsDict())

    def test_trend(self):
        """ Test twitter.Trend object """
        trend = twitter.Trend.NewFromJsonDict(self.TREND_SAMPLE_JSON)
        try:
            trend.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(trend.AsJsonString())
        self.assertTrue(trend.AsDict())
        self.assertEqual(trend.tweet_volume, 104403)
        self.assertEqual(trend.volume, trend.tweet_volume)

    def test_url(self):
        url = twitter.Url.NewFromJsonDict(self.URL_SAMPLE_JSON)
        try:
            url.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(url.AsJsonString())
        self.assertTrue(url.AsDict())

    def test_user(self):
        '''Test the twitter.User NewFromJsonDict method'''
        user = twitter.User.NewFromJsonDict(self.USER_SAMPLE_JSON)
        self.assertEqual(user.id, 718443)
        try:
            user.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(user.AsJsonString())
        self.assertTrue(user.AsDict())
        self.assertTrue(isinstance(user.status, twitter.Status))
        self.assertTrue(isinstance(user.AsDict()['status'], dict))

    def test_user_status(self):
        """ Test twitter.UserStatus object """
        user_status = twitter.UserStatus.NewFromJsonDict(self.USER_STATUS_SAMPLE_JSON)
        try:
            user_status.__repr__()
        except Exception as e:
            self.fail(e)
        self.assertTrue(user_status.AsJsonString())
        self.assertTrue(user_status.AsDict())
