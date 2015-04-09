import json
import re

import mock

from django.test import TestCase, Client

from search.court_search import Postcode, CourtSearchInvalidPostcode, CourtSearchError
from search.postcode_lookups import MapitLookup, AddressFinderLookup #, UkPostcodesLookup

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


class PostcodeTestCase(TestCase):

    def test_full_postcode(self):
        p = Postcode(postcodes['full'])
        self.assertTrue(p.full_postcode)

    def test_partial_postcode(self):
        p = Postcode(postcodes['partial'])
        self.assertTrue(p.partial_postcode)


class MapitLookupTestCase(TestCase):
    mock_mapit_partial = '{"wgs84_lat": 51.47263752259685, "wgs84_lon": -0.06603088421009512, "postcode": "SE15" }'
    mock_mapit_full = """
        {
            "postcode": "SE15 4UH",
            "shortcuts": { "WMC": 65913, "council": 2491, "ward": 8328 },
            "wgs84_lat": 51.468945906164286, "wgs84_lon": -0.06623508303668792,
            "areas": {
                "2491": {
                    "all_names": {},
                    "codes": { "gss": "E09000028", "ons": "00BE", "unit_id": "11013" },
                    "country": "E",
                    "country_name": "England",
                    "generation_high": 22,
                    "generation_low": 1,
                    "id": 2491,
                    "name": "Southwark Borough Council",
                    "parent_area": null,
                    "type": "LBO",
                    "type_name": "London borough"
                }
            }
        }
    """
    mock_mapit_no_location = '{"postcode": "GY1 1AJ", "areas": {}}'    


    def setUp(self):
        self.patcher = mock.patch('requests.get', mock.Mock(side_effect=self._get_from_mapit_mock))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def _get_from_mapit_mock( self, url, headers={} ):
        mock_response = MockResponse()

        if url.endswith('SE15'):
            mock_response.text =  MapitLookupTestCase.mock_mapit_partial
        elif url.endswith('SE15 4UH'):
            mock_response.text =  MapitLookupTestCase.mock_mapit_full
        elif url.endswith('GY1 1AJ'):
            mock_response.text = MapitLookupTestCase.mock_mapit_no_location
        elif url.endswith('Service Down'):
            mock_response.status_code = 500
        else:
            mock_response.status_code = 404

        return mock_response

    def test_latitude(self):
        p = Postcode(postcodes['full'])
        p.lookup_postcode('mapit')
        self.assertEqual(p.latitude, 51.468945906164286)

    def test_longitude(self):
        p = Postcode(postcodes['full'])
        p.lookup_postcode('mapit')
        self.assertEqual(p.longitude, -0.06623508303668792)

    def test_local_authority_support(self):
        mapit = MapitLookup(postcodes['full'])
        self.assertEqual(mapit.supports_local_authority(), True)

    def test_local_authority_name(self):
        p = Postcode(postcodes['full'])
        p.lookup_local_authority(None, 'mapit')
        self.assertEqual(p.local_authority_name, 'Southwark Borough Council')

    def test_no_local_authority_for_partial_postcode(self):
        p = Postcode(postcodes['partial'])
        p.lookup_local_authority(None, 'mapit')
        self.assertIsNone(p.local_authority)

    def test_broken_postcode(self):
        with self.assertRaises(CourtSearchInvalidPostcode):
            p = Postcode(postcodes['broken'])
            p.lookup_postcode('mapit')

    def test_500(self):
        with self.assertRaises(CourtSearchError):
            p = Postcode('Service Down')
            p.lookup_postcode('mapit')

    def test_nowhere_postcode(self):
        with self.assertRaises(CourtSearchInvalidPostcode):
            p = Postcode(postcodes['nowhere'])
            p.lookup_postcode('mapit')


class AddressFinderLookupTestCase(TestCase):
    # TODO:  next
    mock_address_finder_full = """
        {
           "type" : "Point",
           "coordinates" : [
              -1.78826971425321,
              51.5570372347208
           ]
        }
    """

    mock_address_finder_partial = """
        {
            "type": "Point",
            "coordinates": [
                -1.946231306487139,
                53.41723542125218
            ]
        }
    """

    def setUp(self):
        self.patcher = mock.patch('requests.get', mock.Mock(side_effect=self._get_from_address_finder_mock))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def _get_from_address_finder_mock( self, url, headers={} ):
        mock_response = MockResponse()

        if url.endswith('SE15'):
            mock_response.text =  AddressFinderLookupTestCase.mock_address_finder_partial
        elif url.endswith('SE15 4UH'):
            mock_response.text =  AddressFinderLookupTestCase.mock_address_finder_full
        elif url.endswith('GY1 1AJ'):
            mock_response.status_code = 404
        elif url.endswith('Service Down'):
            mock_response.status_code = 500
        else:
            mock_response.status_code = 404

        return mock_response

    def test_latitude(self):
        p = Postcode(postcodes['full'])
        p.lookup_postcode('address_finder')
        self.assertEqual(p.latitude, 51.5570372347208)

    def test_longitude(self):
        p = Postcode(postcodes['full'])
        p.lookup_postcode('address_finder')
        self.assertEqual(p.longitude, -1.78826971425321)

    def test_local_authority_support(self):
        address_finder = AddressFinderLookup(postcodes['full'])
        self.assertEqual(address_finder.supports_local_authority(), False)

    def test_broken_postcode(self):
        with self.assertRaises(CourtSearchInvalidPostcode):
            p = Postcode(postcodes['broken'])
            p.lookup_postcode('address_finder')

    def test_500(self):
        with self.assertRaises(CourtSearchError):
            p = Postcode('Service Down')
            p.lookup_postcode('address_finder')

    def test_nowhere_postcode(self):
        with self.assertRaises(CourtSearchInvalidPostcode):
            p = Postcode(postcodes['nowhere'])
            p.lookup_postcode('address_finder')


