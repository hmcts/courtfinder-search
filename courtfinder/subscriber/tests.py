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

    def test_post_on_url_endpoint_without_data(self):
      # 400 Bad Request - Often missing a required parameter.
      response = self.client.post('/subscriber/update')
      self.assertEqual(response.status_code, 400)

    def test_get_on_url_endpoint(self):
      response = self.client.get('/subscriber/update')
      self.assertEqual(response.status_code, 405)

    def test_post_on_url_endpoint_with_data(self):
      response = self.client.post('/subscriber/update', { "court": '{name": "Abergavenny Magistrates Court"}' })
      self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
