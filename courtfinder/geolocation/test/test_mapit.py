from geolocation import mapit
from django.test import TestCase
from mock import patch, MagicMock


class MapitTestCase(TestCase):

    @patch('requests.get')
    def test_api_call(self, get):
        response = MagicMock
        response.status_code = 200
        response.json = MagicMock(return_value={'test': 1})
        get.return_value = response

        self.assertEqual({'test': 1}, mapit.api_call('/xyz'))
        get.assert_called_once_with('https://mapit.mysociety.org/xyz', headers={'X-Api-Key': None})

    def test_filter_postcode(self):
        self.assertEqual('SW1A1AA', mapit.filter_postcode(lambda(s): True, 'SW1A 1AA'))
        self.assertEqual('SW1A1AA', mapit.filter_postcode(lambda(s): True, 'sw1a 1aa'))
        self.assertEqual('SW1A1AA', mapit.filter_postcode(lambda(s): True, ' sw1a 1aa '))

    def test_filter_validate_exception(self):
        with self.assertRaises(mapit.InvalidPostcode):
            mapit.filter_postcode(lambda(s): False, 'XXX')

    @patch('geolocation.mapit.api_call')
    def test_postcode_call(self, api):
        postcode = mapit.postcode('SW1A 1AA')
        api.assert_called_once_with('/postcode/SW1A1AA')
        self.assertIsInstance(postcode, mapit.Postcode)

    @patch('geolocation.mapit.api_call')
    def test_partial_postcode_call(self, api):
        postcode = mapit.partial_postcode('SW1A')
        api.assert_called_once_with('/postcode/partial/SW1A')
        self.assertIsInstance(postcode, mapit.PartialPostcode)


    def test_coordinates(self):
        data = {'wgs84_lat': 1.0,'wgs84_lon': 0.1, 'postcode': 'test'}
        postcode = mapit.Postcode(data)
        self.assertEqual(postcode.coordinates, (1.0, 0.1))

    def test_local_authority(self):
        data = {'shortcuts': {'council': 111}, 'areas': {'111': {'name': 'test council'}}, 'postcode': 'test'}
        postcode = mapit.Postcode(data)
        self.assertEqual(postcode.local_authority, 'test council')
