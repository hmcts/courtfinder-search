import requests

from django.test import TestCase, Client
from django.core.management import call_command

from search.models import Court

class SearchRegressionTestCase(TestCase):

    def setUp(self):
        call_command('populate-db' )

    def tearDown(self):
        pass

    def test_if_db_populated(self):
        import pdb
        pdb.set_trace()
        
        self.assertGreater(Court.objects.count(), 0)
