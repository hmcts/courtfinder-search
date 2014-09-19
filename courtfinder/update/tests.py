from django.test import TestCase, Client
import requests
from mock import Mock, patch
from search.models import *
from django.conf import settings


class SearchTestCase(TestCase):

    def setUp(self):
        self.court = Court.objects.create(
            admin_id=23,
            name="Example Court",
            lat=0.0,
            lon=0.0,
        )

    def test_modify_court_name(self):
        c = Client()
        new_court_json='{"admin_id":23,"name":"New Name"}'
        response = c.post('/update/court',
                          {'court_data':new_court_json})
        self.assertEqual(response.content, 'OK')
        new_court = Court.objects.get(name="New Name")
        self.assertEqual(new_court.admin_id, 23)

