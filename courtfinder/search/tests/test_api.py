from django.test import Client
from mock import Mock, patch
from courtfinder.test_utils import TestCaseWithData
from search.errors import CourtSearchError


class SearchTestCase(TestCaseWithData):
    def test_county(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertIn('"county": "Lancashire"', response.content)

    def test_postcode(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15+4UH&aol=divorce')
        self.assertEqual(response.status_code, 200)

    def test_postcode_search(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15&aol=divorce')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '"name": "Accrington Magistrates\' Court"', response.content)

    def test_address_search(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '"name": "Accrington Magistrates\' Court"', response.content)

    def test_no_aol(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '"name": "Accrington Magistrates\' Court"', response.content)

    def test_empty_query(self):
        c = Client()
        response = c.get('/search/results.json?q=')
        self.assertEquals(400, response.status_code)

    def test_court_type(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertIn('Magistrates Court', response.content)

    def test_internal_error(self):
        c = Client()
        with patch('search.court_search.CourtSearch.get_courts', Mock(side_effect=CourtSearchError('something went wrong'))):
            response = c.get('/search/results.json?q=Accrington')
            self.assertEquals(500, response.status_code)
            self.assertIn("something went wrong", response.content)
