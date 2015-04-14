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




