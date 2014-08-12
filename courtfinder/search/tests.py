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


class ClientTestCase(unittest.TestCase):
    """Test case for the client methods."""

    def setUp(self):
        self.patcher = patch('search.search_api.urlopen', fake_urlopen)
        self.patcher.start()
        self.client = SearchAPI()

    def tearDown(self):
        self.patcher.stop()

    def test_request(self):
        """Test a simple request."""
        postcode = 'SW1H9AJ'
        response = self.client.request(postcode)
        self.assertIn('name', response)
        self.assertEqual(response['name'], 'Test User')
