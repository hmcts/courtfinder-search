from django.test import TestCase, Client
import requests
from mock import MagicMock, patch
from search.court_search import CourtSearch
from django.conf import settings


class SearchTestCase(TestCase):

    def test_top_page_sans_slash_redirects_to_slash(self):
        c = Client()
        response = c.get('/search')
        self.assertRedirects(response, '/search/', 301)

    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.jinja')
        self.assertInHTML('<title>Find a court or tribunal</title>', response.content, count=1)

    def test_sample_postcode_all_aols(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&area_of_law=All')
        self.assertEqual(response.status_code, 200)

    def test_sample_postcode_specific_aol(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&area_of_law=Divorce')
        self.assertEqual(response.status_code, 200)

    def test_sample_postcode_bad_aol(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&area_of_law=doesntexist')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sorry, there are no results', response.content)

    def test_partial_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15&area_of_law=All')
        self.assertEqual(response.status_code, 200)

    def test_api_postcode(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15+4UH&area_of_law=Bankruptcy')
        self.assertEqual(response.status_code, 200)

    def test_address_search(self):
        c = Client()
        response = c.get('/search/results?q=Leeds')
        self.assertEqual(response.status_code, 200)

    def test_broken_postcode_latlon_mapping(self):
        self.assertEqual(CourtSearch.postcode_search('Z', 'Money'), [])

    def test_broken_mapit(self):
        saved = settings.MAPIT_BASE_URL
        settings.MAPIT_BASE_URL = 'http://broken.example.com/'
        with self.assertRaises(requests.exceptions.ConnectionError):
            CourtSearch.postcode_to_latlon('SE144UR')
        settings.MAPIT_BASE_URL = saved

    def test_mapit_doesnt_return_correct_data(self):
        with patch('search.court_search.CourtSearch.get_from_mapit', MagicMock(return_value="garbage")):
            with self.assertRaises(Exception):
                CourtSearch.postcode_to_latlon('SE154UH')

    def test_bad_aol_on_postcode_search(self):
        self.assertEqual(CourtSearch.postcode_search('SE154UH', 'bad aol'), [])

    def test_working_postcode_search(self):
        self.assertNotEqual(CourtSearch.postcode_search('SE154UH', 'Money claims'), [])

