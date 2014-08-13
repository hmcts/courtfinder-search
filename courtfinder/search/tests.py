from django.test import TestCase

# Create your tests here.
import os.path
import unittest
import urlparse
# from urlparse import urlparse

from search_api import SearchAPI
from mock import patch

def fake_urlopen(url):
    """
    A stub urlopen() implementation that load json responses from
    the filesystem.
    """
    # Map path from url to a file
    parsed_url = urlparse.urlparse(url)
    qs = urlparse.parse_qs(parsed_url.query)
    postcode = qs['postcode'][0]
    area_of_law = qs['area_of_law'][0]

    resource_file_name  = 'tests/resources%s/%s' % (parsed_url.path, postcode + '_' + area_of_law)
    resource_file_name = resource_file_name.replace(" ", "+")

    print 'Fake ULR: Reading file from: %s' % resource_file_name
    # # Must return a file-like object
    return open(resource_file_name)


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('search.search_api.urlopen', fake_urlopen)
        self.patcher.start()
        self.client = SearchAPI()

    def tearDown(self):
        self.patcher.stop()

    def test_finding_courts_for_correct_postcode_and_adoption(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Adoption'

        response = self.client.request(postcode, area_of_law)

        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Inner London Family Proceedings Court')
        self.assertIn('name', response[1])
        self.assertEqual(response[1]['name'], 'Central Family Court')

    def test_finding_courts_for_correct_postcode_and_children(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Children'

        response = self.client.request(postcode, area_of_law)

        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Central Family Court')

    def test_finding_courts_for_correct_postcode_and_civil_parternship(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Civil partnership'

        response = self.client.request(postcode, area_of_law)

        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Central Family Court')

        self.assertIn('name', response[1])
        self.assertEqual(response[1]['name'], 'Brighton Family Court')

    def test_finding_courts_for_correct_postcode_and_divorce(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Divorce'

        response = self.client.request(postcode, area_of_law)

        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Central Family Court')

    def test_finding_courts_for_correct_postcode_and_bankruptcy(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Bankruptcy'

        response = self.client.request(postcode, area_of_law)

        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Royal Courts of Justice')

    def test_finding_courts_for_correct_postcode_and_housing_possession(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Housing possession'

        response = self.client.request(postcode, area_of_law)

        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Central London County Court')

    def test_finding_courts_for_correct_postcode_and_money_claims(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Money Claims'

        response = self.client.request(postcode, area_of_law)

        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Central London County Court')

    def test_finding_courts_for_correct_postcode_and_probate(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Probate'

        response = self.client.request(postcode, area_of_law)
        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'London Probate Department')

        self.assertIn('name', response[1])
        self.assertEqual(response[1]['name'], 'Maidstone Probate Sub-Registry')

    def test_finding_courts_for_correct_postcode_and_crime(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Crime'

        response = self.client.request(postcode, area_of_law)
        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Blackfriars Crown Court')
        self.assertIn('name', response[1])
        self.assertEqual(response[1]['name'], 'Inner London Crown Court')

    def test_finding_courts_for_correct_postcode_and_domestic_violence(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Domestic Violence'

        response = self.client.request(postcode, area_of_law)
        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Lambeth County Court and Family Court')

        self.assertIn('name', response[1])
        self.assertEqual(response[1]['name'], 'Central Family Court')

    def test_finding_courts_for_correct_postcode_and_forced_marriage(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Forced marriage'

        response = self.client.request(postcode, area_of_law)
        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Central Family Court')

        self.assertIn('name', response[1])
        self.assertEqual(response[1]['name'], 'Willesden County Court and Family Court')

    def test_finding_courts_for_correct_postcode_and_employment(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Employment'

        response = self.client.request(postcode, area_of_law)
        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Central London Employment Tribunal')

        self.assertIn('name', response[1])
        self.assertEqual(response[1]['name'], 'Croydon Employment Tribunal')

    def test_finding_courts_for_correct_postcode_and_social_security(self):
        postcode = 'SW1H9AJ'
        area_of_law = 'Social security'

        response = self.client.request(postcode, area_of_law)
        self.assertIn('name', response[0])
        self.assertEqual(response[0]['name'], 'Sutton Social Security and Child Support Tribunal')

        self.assertIn('name', response[1])
        self.assertEqual(response[1]['name'], 'Bexleyheath Social Security and Child Support Tribunal')
