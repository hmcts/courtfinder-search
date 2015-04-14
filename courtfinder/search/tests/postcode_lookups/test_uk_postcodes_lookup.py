import json
import re

import mock

from django.test import TestCase, Client

from search.court_search import Postcode, CourtSearchInvalidPostcode, CourtSearchError
from search.postcode_lookups import UkPostcodesLookup

postcodes = {
    'full': 'SE15 4UH',
    'partial': 'SE15',
    'broken': 'SE15 4',
    'nowhere': 'GY1 1AJ'
}

class MockResponse():
    def __init__(self):
        self.status_code = 200
        self.text = ''


class UkPostcodesLookupTestCase(TestCase):
    mock_uk_postcodes_partial = """
        {
          "code": 404,
          "error": "Postcode SE15 cannot be found"
        }
    """
    mock_uk_postcodes_full = """
        {
          "postcode": "SE15 4UH",
          "geo": {
            "lat": 51.468946011406956,
            "lng": -0.06622068897438116,
            "easting": 534414.0,
            "northing": 176215.0,
            "geohash": "http://geohash.org/gcpuy3xu2fyq"
          },
          "administrative": {
            "council": {
              "title": "Southwark",
              "uri": "http://statistics.data.gov.uk/id/statistical-geography/E09000028",
              "code": "E09000028"
            },
            "ward": {
              "title": "The Lane",
              "uri": "http://statistics.data.gov.uk/id/statistical-geography/E05000553",
              "code": "E05000553"
            },
            "constituency": {
              "title": "Camberwell and Peckham",
              "uri": "http://statistics.data.gov.uk/id/statistical-geography/E14000615",
              "code": "E14000615"
            }
          }
        }
    """
    mock_uk_postcodes_no_location = """
        {
          "postcode": "GY1 1AJ",
          "geo": {
            "lat": 49.76682050222725,
            "lng": -7.557149366696847,
            "easting": 0.0,
            "northing": 0.0,
            "geohash": "http://geohash.org/gbfeh5c09xtp"
          }
        }
    """    


    def setUp(self):
        self.patcher = mock.patch('requests.get', mock.Mock(side_effect=self._get_from_uk_postcodes_mock))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def _get_from_uk_postcodes_mock( self, url, headers={} ):
        mock_response = MockResponse()

        if url.endswith('SE15.json'):
            mock_response.status_code = 404
            mock_response.text =  UkPostcodesLookupTestCase.mock_uk_postcodes_partial
        elif url.endswith('SE15 4UH.json'):
            mock_response.text =  UkPostcodesLookupTestCase.mock_uk_postcodes_full
        elif url.endswith('GY1 1AJ.json'):
            mock_response.text = UkPostcodesLookupTestCase.mock_uk_postcodes_no_location
        elif url.endswith('Service Down'):
            mock_response.status_code = 500
        else:
            mock_response.status_code = 404

        return mock_response

    def test_latitude(self):
        p = Postcode(postcodes['full'])
        p.lookup_postcode('uk_postcodes')
        self.assertEqual(p.latitude, 51.468946011406956)

    def test_longitude(self):
        p = Postcode(postcodes['full'])
        p.lookup_postcode('uk_postcodes')
        self.assertEqual(p.longitude, -0.06622068897438116)

    def test_local_authority_support(self):
        uk_postcodes = UkPostcodesLookup(postcodes['full'])
        self.assertEqual(uk_postcodes.supports_local_authority(), True)

    def test_local_authority_name(self):
        p = Postcode(postcodes['full'])
        p.lookup_local_authority(None, 'uk_postcodes')
        self.assertEqual(p.local_authority_name, 'Southwark')

    def test_local_authority_gss_code(self):
        p = Postcode(postcodes['full'])
        p.lookup_local_authority(None, 'uk_postcodes')
        self.assertEqual(p.local_authority_gss_code, 'E09000028')

    def test_error_for_partial_postcode(self):
      with self.assertRaises(CourtSearchInvalidPostcode):
        p = Postcode(postcodes['partial'])
        p.lookup_local_authority(None, 'uk_postcodes')

    def test_broken_postcode(self):
        with self.assertRaises(CourtSearchInvalidPostcode):
            p = Postcode(postcodes['broken'])
            p.lookup_postcode('uk_postcodes')

    def test_500(self):
        with self.assertRaises(CourtSearchError):
            p = Postcode('Service Down')
            p.lookup_postcode('uk_postcodes')

    def test_nowhere_postcode(self):
        with self.assertRaises(CourtSearchInvalidPostcode):
            p = Postcode(postcodes['nowhere'])
            p.lookup_local_authority(None, 'uk_postcodes')

