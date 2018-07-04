import twitter
import json
import sys
import unittest


class PlaceTest(unittest.TestCase):
    SAMPLE_JSON = '''{"id": "df51dec6f4ee2b2c", "url": "https://api.twitter.com/1.1/geo/id/df51dec6f4ee2b2c.json", "place_type": "neighborhood", "name": "Presidio", "full_name": "Presidio, San Francisco", "country_code": "US", "country": "United States", "contained_within": [{"id": "5a110d312052166f", "url": "https://api.twitter.com/1.1/geo/id/5a110d312052166f.json", "place_type": "city", "name": "San Francisco", "full_name": "San Francisco, CA", "country_code": "US", "country": "United States", "centroid": [-122.4461400159226, 37.759828999999996], "bounding_box": {"type": "Polygon", "coordinates": [[[-122.514926, 37.708075], [-122.514926, 37.833238], [-122.357031, 37.833238], [-122.357031, 37.708075], [-122.514926, 37.708075]]]}, "attributes": {}}], "geometry": null, "polylines": [], "centroid": [-122.46598425785236, 37.79989625], "bounding_box": {"type": "Polygon", "coordinates": [[[-122.4891333, 37.786925], [-122.4891333, 37.8128675], [-122.446306, 37.8128675], [-122.446306, 37.786925], [-122.4891333, 37.786925]]]}, "attributes": {"geotagCount": "6", "162834:id": "2202"}}'''

    def _GetSampleContainedPlace(self):
        return twitter.Place(id='5a110d312052166f',
                             url='https://api.twitter.com/1.1/geo/id/5a110d312052166f.json',
                             place_type='city',
                             name='San Franciso',
                             full_name='San Francisco, CA',
                             country_code='US',
                             country='United States',
                             centroid=[-122.4461400159226,
                                       37.759828999999996],
                             bounding_box=dict(
                                 type='Polygon',
                                 coordinates=[
                                     [
                                         [-122.514926, 37.708075],
                                         [-122.514926, 37.833238],
                                         [-122.357031, 37.833238],
                                         [-122.357031, 37.708075],
                                         [-122.514926, 37.708075]
                                     ]
                                 ],
                                 attributes=dict()
                             )
                         )

    def _GetSamplePlace(self):
        return twitter.Place(id='df51dec6f4ee2b2c',
                             url='https://api.twitter.com/1.1/geo/id/df51dec6f4ee2b2c.json',
                             place_type='neighborhood',
                             name='Presidio',
                             full_name='Presidio, San Francisco',
                             country_code='US',
                             country='United States',
                             contained_within=[
                                 self._GetSampleContainedPlace()
                             ],
                             geometry='null',
                             polylines=[],
                             centroid=[-122.46598425785236, 37.79989625],
                             bounding_box=dict(
                                 type='Polygon',
                                 coordinates=[
                                     [
                                         [-122.4891333, 37.786925],
                                         [-122.4891333, 37.8128675],
                                         [-122.446306, 37.8128675],
                                         [-122.446306, 37.786925],
                                         [-122.4891333, 37.786925]
                                     ]
                                 ]
                             ),
                             attributes={
                                 'geotagCount': '6',
                                 '162834:id': '2202'
                             }
                             )

    def testProperties(self):
        '''Test all of the twitter.Place properties'''
        place = twitter.Place()
        place.id = 'df51dec6f4ee2b2c'
        self.assertEqual('df51dec6f4ee2b2c', place.id)
        place.name = 'Presidio'
        self.assertEqual('Presidio', place.name)
        place.full_name = 'Presidio, San Francisco'
        self.assertEqual('Presidio, San Francisco', place.full_name)
        place.country_code = 'US'
        self.assertEqual('US', place.country_code)
        place.country = 'United States'
        self.assertEqual('United States', place.country)
        place.url = 'https://api.twitter.com/1.1/geo/id/df51dec6f4ee2b2c.json'
        self.assertEqual('https://api.twitter.com/1.1/geo/id/df51dec6f4ee2b2c.json', place.url)
        place.contained_within = [self._GetSampleContainedPlace()]
        self.assertEqual('5a110d312052166f', place.contained_within[0].id)

    @unittest.skipIf(sys.version_info.major >= 3, "skipped until fix found for v3 python")
    def testAsJsonString(self):
        '''Test the twitter.Place AsJsonString method'''
        self.assertEqual(PlaceTest.SAMPLE_JSON,
                         self._GetSamplePlace().AsJsonString())

    def testAsDict(self):
        '''Test the twitter.Place AsDict method'''
        place = self._GetSamplePlace()
        data = place.AsDict()
        self.assertEqual('df51dec6f4ee2b2c', data['id'])
        self.assertEqual('Presidio', data['name'])
        self.assertEqual('Presidio, San Francisco', data['full_name'])
        self.assertEqual('US', data['country_code'])
        self.assertEqual('United States', data['country'])
        self.assertEqual('https://api.twitter.com/1.1/geo/id/df51dec6f4ee2b2c.json', data['url'])

    def testEq(self):
        '''Test the twitter.Place __eq__ method'''
        place = twitter.Place()
        place.id = 'df51dec6f4ee2b2c'
        place.name = 'Presidio'
        place.full_name = 'Presidio, San Francisco'
        place.country_code = 'US'
        place.country = 'United States'
        place.url = 'https://api.twitter.com/1.1/geo/id/df51dec6f4ee2b2c.json'
        place.place_type = 'neighborhood'
        place.centroid = [-122.4461400159226, 37.759828999999996]
        place.geometry = 'null'
        place.polylines = []
        place.bounding_box = dict(type='Polygon',
                                  coordinates=[
                                      [
                                          [-122.4891333, 37.786925],
                                          [-122.4891333, 37.8128675],
                                          [-122.446306, 37.8128675],
                                          [-122.446306, 37.786925],
                                          [-122.4891333, 37.786925]
                                      ]
                                  ]
                                  )
        place.attributes = {
            'geotagCount': '6',
            '162834:id': '2202'
        }
        self.assertEqual(place, self._GetSamplePlace())

    def testHash(self):
        '''Test the twitter.Place __hash__ method'''
        place = self._GetSamplePlace()
        self.assertEqual(hash(place), hash(place.id))

    def testNewFromJsonDict(self):
        '''Test the twitter.Status NewFromJsonDict method'''
        data = json.loads(PlaceTest.SAMPLE_JSON)
        place = twitter.Place.NewFromJsonDict(data)
        self.assertEqual(self._GetSamplePlace(), place)
