import twitter
import unittest
import json


class TrendTest(unittest.TestCase):
    SAMPLE_JSON = '''{"name": "Kesuke Miyagi", "query": "Kesuke Miyagi"}'''

    def _GetSampleTrend(self):
        return twitter.Trend(name='Kesuke Miyagi',
                             query='Kesuke Miyagi',
                             timestamp='Fri Jan 26 23:17:14 +0000 2007')

    def testInit(self):
        '''Test the twitter.Trend constructor'''
        twitter.Trend(name='Kesuke Miyagi',
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
        data = json.loads(TrendTest.SAMPLE_JSON)
        trend = twitter.Trend.NewFromJsonDict(data, timestamp='Fri Jan 26 23:17:14 +0000 2007')
        self.assertEqual(self._GetSampleTrend(), trend)

    def testEq(self):
        '''Test the twitter.Trend __eq__ method'''
        trend = twitter.Trend()
        trend.name = 'Kesuke Miyagi'
        trend.query = 'Kesuke Miyagi'
        trend.timestamp = 'Fri Jan 26 23:17:14 +0000 2007'
        self.assertEqual(trend, self._GetSampleTrend())
