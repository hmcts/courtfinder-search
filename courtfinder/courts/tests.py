import json
import lxml.html
import pprint
import re
import requests

import cssselect
from django.conf import settings
from django.test import TestCase, Client
from lxml import html as lh
from mock import Mock, patch

from search.court_search import CourtSearch, CourtSearchError, CourtSearchInvalidPostcode
from search.ingest import Ingest
from search.models import *


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

    def test_court_emails_are_in_order(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        document = lxml.html.fromstring(response.content)
        first = document.cssselect('.email-label span')[0].text_content()
        second = document.cssselect('.email-label span')[1].text_content()
        self.assertIn('Mediation', first)
        self.assertIn('Enquiries', second)

    def test_court_numbers_in_details_page(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')

        document = lxml.html.fromstring(response.content)
        text = document.cssselect('#pros dl')[0].text_content()

        self.assertIn('Crown Court location code', text)
        self.assertIn('1725', text)
        self.assertIn('County Court location code', text)
        self.assertIn('242', text)
        self.assertIn('Magistrates\' Court location code', text)
        self.assertIn('1337', text)

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

    def test_no_addresses(self):
        c = Client()
        response = c.get('/courts/no-addresses')
        self.assertNotIn('Visit us:', response.content)
        self.assertNotIn('Write to us:', response.content)
        self.assertNotIn('Visit or write to us', response.content)
        self.assertNotIn('Maps and directions', response.content)

    def test_visit_address(self):
        c = Client()
        response = c.get('/courts/visiting-address')
        self.assertIn('Visit us:', response.content)
        self.assertNotIn('Write to us:', response.content)
        self.assertNotIn('Visit or write to us', response.content)
        self.assertIn('Maps and directions', response.content)

    def test_postal_address(self):
        c = Client()
        response = c.get('/courts/postal-address')
        self.assertNotIn('Visit us:', response.content)
        self.assertIn('Write to us:', response.content)
        self.assertNotIn('Visit or write to us', response.content)
        self.assertNotIn('Maps and directions', response.content)

    def test_both_address(self):
        c = Client()
        response = c.get('/courts/both-postal-and-visiting-addresses')
        self.assertIn('Visit us:', response.content)
        self.assertIn('Write to us:', response.content)
        self.assertNotIn('Visit or write to us', response.content)
        self.assertIn('Maps and directions', response.content)

    def test_postal_and_visit_address(self):
        c = Client()
        response = c.get('/courts/postal-and-visiting-address')
        self.assertNotIn('Visit us:', response.content)
        self.assertIn('Visit or write to us', response.content)
        self.assertIn('Maps and directions', response.content)

    def test_leaflet_links_for_magistrates_court(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=True):
            c = Client()
            response = c.get('/courts/leaflet-magistrates-court')
            self.assertIn('Venue details for printing', response.content)
            self.assertIn('Witness for prosecution information for printing', response.content)
            self.assertIn('Witness for defence information for printing', response.content)
            self.assertNotIn('Juror information for printing', response.content)

    def test_leaflet_links_for_crown_courts(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=True):
            c = Client()
            response = c.get('/courts/leaflet-crown-court')
            self.assertIn('Venue details for printing', response.content)
            self.assertIn('Witness for prosecution information for printing', response.content)
            self.assertIn('Witness for defence information for printing', response.content)
            self.assertIn('Juror information for printing', response.content)

    def test_leaflet_links_for_non_magistrate_or_non_crown_courts(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=True):
            c = Client()
            response = c.get('/courts/county-court-money-claims-centre-ccmcc')
            self.assertIn('Venue details for printing', response.content)
            self.assertNotIn('Witness for prosecution information for printing', response.content)
            self.assertNotIn('Witness for defence information for printing', response.content)
            self.assertNotIn('Juror information for printing', response.content)

    def test_court_image_url_is_based_on_settings(self):
        with self.settings(COURT_IMAGE_BASE_URL='http://example.com/images/'):
            c = Client()
            response = c.get('/courts/tameside-magistrates-court')
            self.assertIn("http://example.com/images/tameside_magistrates_court.jpg", response.content)

    def test_leaflet_section_shown_when_enabled(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=True):
            c = Client()
            response = c.get('/courts/leaflet-magistrates-court')
            self.assertIn('Leaflets for printing', response.content)

    def test_leaflet_section_not_shown_when_disabled(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=False):
            c = Client()
            response = c.get('/courts/leaflet-magistrates-court')
            self.assertNotIn('Leaflets for printing', response.content)

    def test_court_opening_times_are_ordered(self):
        client = Client()

        response1 = client.get("/courts/old-open-court-still-in-use")
        response2 = client.get("/courts/Hide_AoLs")
        dom1 = lxml.html.fromstring(response1.content)
        dom2 = lxml.html.fromstring(response2.content)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            [
                i.text
                for i in dom1.cssselect('div#opening-times ul li time')
            ],
            ["a", "b", "c"])
        self.assertEqual(
            [
                i.text
                for i in dom2.cssselect('div#opening-times ul li time')
            ],
            ["c", "b", "d"])

    def test_jury_servive_link_not_shown_on_non_crown_court(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertNotIn('About jury service', response.content)

    def test_jury_service_link_shown_on_crown_court(self):
        c = Client()
        response = c.get('/courts/leaflet-crown-court')
        self.assertIn('About jury service', response.content)
