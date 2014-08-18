from django.test import TestCase

import os.path
import unittest
import urlparse
from django.test.client import Client

# Create your tests here.


class SubscriberTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    # def tearDown(self):

    def test_url_endpoint(self):
      response = self.client.post('/subscriber/update', {'username': 'john', 'password': 'smith'})
      self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
