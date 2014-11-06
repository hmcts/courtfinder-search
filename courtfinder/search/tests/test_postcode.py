import json
import re

import mock

from django.test import TestCase, Client

from search.court_search import Postcode, CourtSearchInvalidPostcode, CourtSearchError

class MockResponse():
    def __init__(self):
        self.status_code = 200
        self.text = ''


class PostcodeTestCase(TestCase):
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

    full_postcode = 'SE15 4UH'
    partial_postcode = 'SE15'
    broken_postcode = 'SE15 4'
    nowhere_postcode = 'GY1 1AJ'

    def setUp(self):
        self.patcher = mock.patch('requests.get', mock.Mock(side_effect=self._get_from_mapit_mock))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def _get_from_mapit_mock( self, url ):
        mock_response = MockResponse()

        if url.endswith('SE15'):
            mock_response.text =  PostcodeTestCase.mock_mapit_partial
        elif url.endswith('SE15 4UH'):
            mock_response.text =  PostcodeTestCase.mock_mapit_full
        elif url.endswith('GY1 1AJ'):
            mock_response.text = PostcodeTestCase.mock_mapit_no_location
        elif url.endswith('Service Down'):
            mock_response.status_code = 500
        else:
            mock_response.status_code = 404

        return mock_response


    def test_full_postcode(self):
        p = Postcode(self.full_postcode)
        self.assertTrue(p.full_postcode)

    def test_partial_postcode(self):
        p = Postcode(self.partial_postcode)
        self.assertTrue(p.partial_postcode)

#    def test_local_authority(self):
#        p = Postcode(self.full_postcode)
#        self.assertEqual(p.local_authority, 'Southwark Borough Council')

    def test_no_local_authority_for_partial_postcode(self):
        p = Postcode(self.partial_postcode)
        self.assertIsNone(p.local_authority)

    def test_broken_postcode(self):
        self.assertRaises(CourtSearchInvalidPostcode, Postcode, self.broken_postcode)

    def test_500(self):
        self.assertRaises(CourtSearchError, Postcode, 'Service Down')

    def test_nowhere_postcode(self):
        with self.assertRaises(CourtSearchInvalidPostcode):
            p = Postcode(self.nowhere_postcode)
