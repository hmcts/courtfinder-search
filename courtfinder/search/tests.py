from django.test import TestCase

# Create your tests here.
import os.path
import unittest
from urlparse import urlparse

from client import ClientAPI
from mock import patch

def fake_urlopen(url):
    """
    A stub urlopen() implementation that load json responses from
    the filesystem.
    """
    # Map path from url to a file
    parsed_url = urlparse(url)
    resource_file = os.path.normpath('tests/resources%s' % parsed_url.path)
    # Must return a file-like object
    return open(resource_file, mode='rb')


class ClientTestCase(unittest.TestCase):
    """Test case for the client methods."""

    def setUp(self):
        self.patcher = patch('search.client.urlopen', fake_urlopen)
        self.patcher.start()
        self.client = ClientAPI()

    def tearDown(self):
        self.patcher.stop()

    def test_request(self):
        """Test a simple request."""
        user = 'test_user'
        response = self.client.request(user)
        self.assertIn('name', response)
        self.assertEqual(response['name'], 'Test User')
