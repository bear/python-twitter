# -*- coding: utf-8 -*-

import json
import unittest

import twitter


class MediaTest(unittest.TestCase):
    SIZES = {'large': {'h': 175, 'resize': 'fit', 'w': 333},
             'medium': {'h': 175, 'resize': 'fit', 'w': 333},
             'small': {'h': 175, 'resize': 'fit', 'w': 333},
             'thumb': {'h': 150, 'resize': 'crop', 'w': 150}}
    RAW_JSON = '''{"display_url": "pic.twitter.com/lX5LVZO", "expanded_url": "http://twitter.com/fakekurrik/status/244204973972410368/photo/1", "id": 244204973989187584, "id_str": "244204973989187584", "indices": [44,63], "media_url": "http://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png", "media_url_https": "https://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png", "sizes": {"large": {"h": 175, "resize": "fit", "w": 333}, "medium": {"h": 175, "resize": "fit", "w": 333}, "small": {"h": 175, "resize": "fit", "w": 333}, "thumb": {"h": 150, "resize": "crop", "w": 150}}, "type": "photo", "url": "http://t.co/lX5LVZO"}'''
    SAMPLE_JSON = '''{"display_url": "pic.twitter.com/lX5LVZO", "expanded_url": "http://twitter.com/fakekurrik/status/244204973972410368/photo/1", "id": 244204973989187584, "media_url": "http://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png", "media_url_https": "https://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png", "sizes": {"large": {"h": 175, "resize": "fit", "w": 333}, "medium": {"h": 175, "resize": "fit", "w": 333}, "small": {"h": 175, "resize": "fit", "w": 333}, "thumb": {"h": 150, "resize": "crop", "w": 150}}, "type": "photo", "url": "http://t.co/lX5LVZO"}'''

    def _GetSampleMedia(self):
        return twitter.Media(
            id=244204973989187584,
            expanded_url='http://twitter.com/fakekurrik/status/244204973972410368/photo/1',
            display_url='pic.twitter.com/lX5LVZO',
            url='http://t.co/lX5LVZO',
            media_url_https='https://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png',
            media_url='http://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png',
            sizes=MediaTest.SIZES,
            type='photo')

    def testInit(self):
        '''Test the twitter.Media constructor'''
        media = twitter.Media(
            id=244204973989187584,
            display_url='pic.twitter.com/7a2z7S8tKL',
            expanded_url='http://twitter.com/NASAJPL/status/672830989895254016/photo/1',
            url='https://t.co/7a2z7S8tKL',
            media_url_https='https://pbs.twimg.com/media/CVZgOC3UEAELUcL.jpg',
            media_url='http://pbs.twimg.com/media/CVZgOC3UEAELUcL.jpg',
            type='photo')

    def testProperties(self):
        '''Test all of the twitter.Media properties'''
        media = twitter.Media()

        media.id = 244204973989187584
        media.display_url = 'pic.twitter.com/7a2z7S8tKL'
        media.expanded_url = 'http://twitter.com/NASAJPL/status/672830989895254016/photo/1'
        media.url = 'https://t.co/7a2z7S8tKL'
        media.media_url_https = 'https://pbs.twimg.com/media/CVZgOC3UEAELUcL.jpg'
        media.media_url = 'http://pbs.twimg.com/media/CVZgOC3UEAELUcL.jpg'
        media.type = 'photo'

        self.assertEqual('pic.twitter.com/7a2z7S8tKL', media.display_url)
        self.assertEqual(
            'http://twitter.com/NASAJPL/status/672830989895254016/photo/1',
            media.expanded_url)
        self.assertEqual('https://t.co/7a2z7S8tKL', media.url)
        self.assertEqual(
            'https://pbs.twimg.com/media/CVZgOC3UEAELUcL.jpg',
            media.media_url_https)
        self.assertEqual(
            'http://pbs.twimg.com/media/CVZgOC3UEAELUcL.jpg',
            media.media_url)
        self.assertEqual('photo', media.type)

    def testAsJsonString(self):
        '''Test the twitter.User AsJsonString method'''
        self.assertEqual(MediaTest.SAMPLE_JSON,
                         self._GetSampleMedia().AsJsonString())

    def testAsDict(self):
        '''Test the twitter.Media AsDict method'''
        media = self._GetSampleMedia()
        data = media.AsDict()

        self.assertEqual(
            'pic.twitter.com/lX5LVZO',
            data['display_url'])
        self.assertEqual(
            'http://twitter.com/fakekurrik/status/244204973972410368/photo/1',
            data['expanded_url'])
        self.assertEqual('http://t.co/lX5LVZO', data['url'])
        self.assertEqual(
            'https://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png',
            data['media_url_https'])
        self.assertEqual(
            'http://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png',
            data['media_url'])

        self.assertEqual('photo', data['type'])

    def testEq(self):
        '''Test the twitter.Media __eq__ method'''
        media = twitter.Media()
        media.id = 244204973989187584
        media.display_url = 'pic.twitter.com/lX5LVZO'
        media.expanded_url = 'http://twitter.com/fakekurrik/status/244204973972410368/photo/1'
        media.url = 'http://t.co/lX5LVZO'
        media.media_url_https = 'https://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png'
        media.media_url = 'http://pbs.twimg.com/media/A2OXIUcCUAAXj9k.png'
        media.type = 'photo'
        media.sizes = MediaTest.SIZES

        self.assertEqual(media, self._GetSampleMedia())

    def testHash(self):
        '''Test the twitter.Media __hash__ method'''
        media = self._GetSampleMedia()
        self.assertEqual(hash(media), hash(media.id))

    def testNewFromJsonDict(self):
        '''Test the twitter.Media NewFromJsonDict method'''
        data = json.loads(MediaTest.RAW_JSON)
        media = twitter.Media.NewFromJsonDict(data)
        self.assertEqual(self._GetSampleMedia(), media)

    def test_media_info(self):
        with open('testdata/get_status_promoted_video_tweet.json', 'r') as f:
            tweet = twitter.Status.NewFromJsonDict(json.loads(f.read()))
        media = tweet.media[0]
        self.assertTrue(isinstance(tweet.media, list))
        self.assertTrue(media.video_info)
        self.assertTrue(media.video_info.get('variants', None))
        self.assertTrue(
            media.video_info.get('variants', None)[0]['url'],
            'https://video.twimg.com/amplify_video/778025997606105089/vid/320x180/5Qr0z_HeycC2DvRj.mp4')
