import pprint
import requests
import json
import re
from django.test import TestCase, Client
from mock import Mock, patch
from search.court_search import CourtSearch, CourtSearchError, CourtSearchInvalidPostcode
from search.models import *
from django.conf import settings
from search.ingest import Ingest


class SearchTestCase(TestCase):

    def setUp(self):
        test_data_dir = settings.PROJECT_ROOT +  '/data/test_data/'
        courts_json_1 = open(test_data_dir + 'courts.json').read()
        imports = json.loads(courts_json_1)
        Ingest.courts(imports['courts'])
        Ingest.emergency_message(imports['emergency_message'])

    def test_sample_court_page(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-court')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tameside", response.content)

    def test_sample_court_page_2(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accrington", response.content)

    def test_court_list_a(self):
        c = Client()
        response = c.get('/courts/A')
        self.assertIn("Names starting with A", response.content)

    def test_court_list_x_no_courts(self):
        c = Client()
        response = c.get('/courts/X')
        self.assertIn("There are no courts or tribunals starting with X", response.content)

    def test_court_list_index(self):
        c = Client()
        response = c.get('/courts/')
        self.assertIn("Select the first letter of the court's name", response.content)

    def test_court_with_email_without_description(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertNotIn('<span property="contactType"></span>', response.content)

    def test_court_numbers_in_list(self):
        c = Client()
        response = c.get('/courts/A')
        self.assertIn('(#1725, CCI: 242)', response.content)

    def test_updated_in_court_page(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertIn('Last updated: 16 April 2014', response.content)

    def test_alert_visible(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertNotIn('class="alert"', response.content)

    def test_alert_whitespace(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-court')
        self.assertIn('class="alert"', response.content)

    def test_blue_badge_displayed(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-court')
        self.assertIn('On site parking is not available at this venue.',
                      response.content)
        self.assertIn('Paid off site parking is available.',
                      response.content)
        self.assertIn('Blue badge parking is available on site.',
                      response.content)

    def test_court_404(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-c0urt')
        self.assertEquals(404, response.status_code)
        self.assertIn('Page not found.',response.content)

    def inactive_court_shows_inactive(self):
        c = Client()
        response = c.get('/courts/old-court-no-longer-in-use')
        self.assertEquals(200, response.status_code)
        self.assertIn('This court or tribunal is no longer in service.',response.content)

    def test_courts_cases_heard_hide_aols(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Cases heard at this venue', response.content)

    def test_courts_cases_heard_show_aols(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-court')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cases heard at this venue', response.content)

    def test_contact_show_explanation(self):
        c = Client()
        response = c.get('/courts/old-open-court-still-in-use')
        self.assertIn('Test explanation', response.content)
