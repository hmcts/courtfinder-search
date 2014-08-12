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
