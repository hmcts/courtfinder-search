import json
import os
from django.test import TestCase
from django.conf import settings
from search.ingest import Ingest
from search.models import DataStatus


class TestCaseWithData(TestCase):
    def setUp(self):
        test_data_path = os.path.join(settings.PROJECT_ROOT, 'data', 'test_data', 'courts.json')
        with open(test_data_path) as f:
            courts_json = f.read()
        Ingest.courts(json.loads(courts_json))
        DataStatus.objects.create(data_hash='6f115002ec6ed1745df7d676d10030fe')
