from django.core.management import call_command
from django.test import TestCase


class TestCaseWithData(TestCase):
    def setUp(self):
        call_command('populate-db', datadir='data/test_data', verbosity='0', ingest='0')
