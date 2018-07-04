import requests
import re
from django.test import TestCase, Client
from mock import Mock, patch
from search.court_search import CourtSearch, CourtSearchError, CourtSearchInvalidPostcode
from search.models import *
from django.conf import settings
from django.core import management
from django.core.management.commands import loaddata


class SearchTestCase(TestCase):

    def setUp(self):
        test_data_dir = settings.PROJECT_ROOT + '/data/test_data/'
        management.call_command('loaddata', test_data_dir + 'test_data.yaml', verbosity=0)

    def tearDown(self):
        pass

    def test_postcode(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15+4UH&aol=Divorce')
        self.assertEqual(response.status_code, 200)

    def test_postcode_search(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE154UH&aol=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

    def test_address_search(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

    def test_no_aol(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE154UH')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

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
