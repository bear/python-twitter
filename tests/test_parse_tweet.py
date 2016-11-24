# encoding: utf-8

import unittest
import twitter


class ParseTest(unittest.TestCase):
    """ Test the ParseTweet class """

    def testParseTweets(self):
        handles4 = u"""Do not use this word! Hurting me! @raja7727: @qadirbasha @manion @Jayks3 உடன்பிறப்பு”"""

        data = twitter.ParseTweet("@twitter", handles4)
        self.assertEqual([data.RT, data.MT, len(data.UserHandles)], [False, False, 4])

        hashtag_n_URL = u"""மனதிற்கு மிகவும் நெருக்கமான பாடல்! உயிரையே கொடுக்கலாம் சார்! #KeladiKanmani https://www.youtube.com/watch?v=FHTiG_g2fM4 … #HBdayRajaSir"""

        data = twitter.ParseTweet("@twitter", hashtag_n_URL)
        self.assertEqual([len(data.Hashtags), len(data.URLs)], [2, 1])
        self.assertEqual(len(data.Emoticon), 0)

        url_only = u"""The #Rainbow #Nebula, 544,667 #lightyears away. pic.twitter.com/2A4wSUK25A"""
        data = twitter.ParseTweet("@twitter", url_only)
        self.assertEqual([data.MT, len(data.Hashtags), len(data.URLs)], [False, 3, 1])
        self.assertEqual(len(data.Emoticon), 0)

        url_handle = u"""RT ‏@BarackObama POTUS recommends Python-Twitter #unrelated picture pic.twitter.com/w8lFIfuUmI"""
        data = twitter.ParseTweet("@twitter", url_handle)
        self.assertEqual([data.RT, len(data.Hashtags), len(data.URLs), len(data.UserHandles)], [True, 1, 1, 1])
        self.assertEqual(len(data.Emoticon), 0)

    def testEmoticon(self):
        url_handle = u"""RT ‏@BarackObama POTUS recommends :-) Python-Twitter #unrelated picture pic.twitter.com/w8lFIfuUmI"""
        data = twitter.ParseTweet("@twitter", url_handle)
        self.assertEqual([data.RT, len(data.Hashtags), len(data.URLs), len(data.UserHandles)], [True, 1, 1, 1])
        self.assertEqual(len(data.Emoticon), 1)

        url_handle = u"""RT @cats ^-^ cute! But kitty litter :-( #unrelated picture"""
        data = twitter.ParseTweet("@cats", url_handle)
        self.assertEqual([data.RT, len(data.Hashtags), len(data.URLs), len(data.UserHandles)], [True, 1, 0, 1])
        self.assertEqual(len(data.Emoticon), 2)
        self.assertEqual(data.Emoticon, ['^-^', ':-('])
