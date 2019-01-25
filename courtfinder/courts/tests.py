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
from django.core import management
from django.core.management.commands import loaddata
from search.models import *


class SearchTestCase(TestCase):

    def setUp(self):
        test_data_dir = settings.PROJECT_ROOT + '/data/test_data/'
        management.call_command('loaddata', test_data_dir + 'test_data.yaml', verbosity=0)

    def test_sample_court_page(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-court')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tameside")

    def test_sample_court_page_2(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accrington")

    def test_court_list_a(self):
        c = Client()
        response = c.get('/courts/A')
        self.assertContains(response, "Names starting with A")

    def test_court_list_x_no_courts(self):
        c = Client()
        response = c.get('/courts/X')
        self.assertContains(response, "There are no courts or tribunals starting with X")

    def test_court_list_index(self):
        c = Client()
        response = c.get('/courts/')
        self.assertContains(response, "Select the first letter of the court's name")

    def test_court_with_email_without_description(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertNotContains(response, '<span property="contactType"></span>')

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
        self.assertNotContains(response, 'class="alert"')

    def test_alert_whitespace(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-court')
        self.assertContains(response, 'class="alert"')

    def test_court_404(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-c0urt')
        self.assertContains(response, 'Page not found', status_code=404)

    def inactive_court_shows_inactive(self):
        c = Client()
        response = c.get('/courts/old-court-no-longer-in-use')
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'This court or tribunal is no longer in service.')

    def test_courts_cases_heard_hide_aols(self):
        c = Client()
        response = c.get('/courts/accrington-magistrates-court')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Cases heard at this venue')

    def test_courts_cases_heard_show_aols(self):
        c = Client()
        response = c.get('/courts/tameside-magistrates-court')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cases heard at this venue')

    def test_contact_show_explanation(self):
        c = Client()
        response = c.get('/courts/old-open-court-still-in-use')
        self.assertContains(response, 'Test explanation')

    def test_no_addresses(self):
        c = Client()
        response = c.get('/courts/no-addresses')
        self.assertNotContains(response, 'Visit us:')
        self.assertNotContains(response, 'Write to us:')
        self.assertNotContains(response, 'Visit or write to us')
        self.assertNotContains(response, 'Maps and directions')

    def test_visit_address(self):
        c = Client()
        response = c.get('/courts/visiting-address')
        self.assertContains(response, 'Visit us:')
        self.assertNotContains(response, 'Write to us:')
        self.assertNotContains(response, 'Visit or write to us')
        self.assertContains(response, 'Maps and directions')

    def test_postal_address(self):
        c = Client()
        response = c.get('/courts/postal-address')
        self.assertNotContains(response, 'Visit us:')
        self.assertContains(response, 'Write to us:')
        self.assertNotContains(response, 'Visit or write to us')
        self.assertNotContains(response, 'Maps and directions')

    def test_both_address(self):
        c = Client()
        response = c.get('/courts/both-postal-and-visiting-addresses')
        self.assertContains(response, 'Visit us:')
        self.assertContains(response, 'Write to us:')
        self.assertNotContains(response, 'Visit or write to us')
        self.assertContains(response, 'Maps and directions')

    def test_postal_and_visit_address(self):
        c = Client()
        response = c.get('/courts/postal-and-visiting-address')
        self.assertNotContains(response, 'Visit us:')
        self.assertContains(response, 'Visit or write to us')
        self.assertContains(response, 'Maps and directions')

    def test_leaflet_links_for_magistrates_court(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=True):
            c = Client()
            response = c.get('/courts/leaflet-magistrates-court')
            self.assertContains(response, 'Venue details for printing')
            self.assertContains(response, 'Witness for prosecution information for printing')
            self.assertContains(response, 'Witness for defence information for printing')
            self.assertNotContains(response, 'Juror information for printing')

    def test_leaflet_links_for_crown_courts(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=True):
            c = Client()
            response = c.get('/courts/leaflet-crown-court')
            self.assertContains(response, 'Venue details for printing')
            self.assertContains(response, 'Witness for prosecution information for printing')
            self.assertContains(response, 'Witness for defence information for printing')
            self.assertContains(response, 'Juror information for printing')

    def test_leaflet_links_for_non_magistrate_or_non_crown_courts(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=True):
            c = Client()
            response = c.get('/courts/county-court-money-claims-centre-ccmcc')
            self.assertContains(response, 'Venue details for printing')
            self.assertNotContains(response, 'Witness for prosecution information for printing')
            self.assertNotContains(response, 'Witness for defence information for printing')
            self.assertNotContains(response, 'Juror information for printing')

    def test_court_image_url_is_based_on_settings(self):
        with self.settings(COURT_IMAGE_BASE_URL='http://example.com/images/'):
            c = Client()
            response = c.get('/courts/tameside-magistrates-court')
            self.assertContains(response, "http://example.com/images/tameside_magistrates_court.jpg")

    def test_leaflet_section_shown_when_enabled(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=True):
            c = Client()
            response = c.get('/courts/leaflet-magistrates-court')
            self.assertContains(response, 'Leaflets for printing')

    def test_leaflet_section_not_shown_when_disabled(self):
        with self.settings(FEATURE_LEAFLETS_ENABLED=False):
            c = Client()
            response = c.get('/courts/leaflet-magistrates-court')
            self.assertNotContains(response, 'Leaflets for printing')

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
        self.assertNotContains(response, 'About jury service')

    def test_jury_service_link_shown_on_crown_court(self):
        c = Client()
        response = c.get('/courts/leaflet-crown-court')
        self.assertContains(response, 'About jury service')
