from django.test import TestCase

import os.path
import unittest
import urlparse

# Create your tests here.

#  curl localhost:3000/update/ --POST {"name": "something" }
#  returns 200

class SubscriberTestCase(unittest.TestCase):
    # def setUp(self):
        # self.patcher = patch('search.search_api.urlopen', fake_urlopen)
        # self.patcher.start()
        # self.client = SearchAPI()

    # def tearDown(self):
        # self.patcher.stop()

    def test_url_endpoint(self):
      self.assertEqual('different', 'is different')

if __name__ == '__main__':
    unittest.main()
