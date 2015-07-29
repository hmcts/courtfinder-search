from django.core.management import call_command
from django.test import TestCase

from search.models import DataStatus


class TestCaseWithData(TestCase):
    def setUp(self):
        call_command('populate-db', 'data/test_data', verbosity='0')
        DataStatus.objects.create(data_hash='6f115002ec6ed1745df7d676d10030fe')
