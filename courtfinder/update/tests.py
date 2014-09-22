from django.test import TestCase, Client
import requests
from mock import Mock, patch
from search.models import *
from django.conf import settings
from update import court_import

class SearchTestCase(TestCase):

    def setUp(self):
        self.court1 = court_import(self.court1_json)

    def test_modify_court_name(self):
        c = Client()
        new_court_json='{"admin_id":23,"name":"New Name"}'
        response = c.post('/update/court',
                          {'court_data':new_court_json})
        self.assertEqual(response.content, 'OK')
        new_court = Court.objects.get(name="New Name")
        self.assertEqual(new_court.admin_id, 23)

    self.court1_json = """
    {
        "addresses": [
            {
                "town": "Accrington",
                "type": "Visiting",
                "postcode": "BB5 2BH",
                "address": "East Lancashire Magistrates' Court\nThe Law Courts\nManchester Road\n"
            },
            {
                "town": "Blackburn",
                "type": "Postal",
                "postcode": "BB2 1AA",
                "address": "Accrington Magistrates' Court\nThe Court House \nNorthgate\t\n"
            }
        ],
        "admin_id": 2800,
        "lat": "53.7491281247251",
        "slug": "accrington-magistrates-court",
        "court_types": [
            "Magistrates Court"
        ],
        "name": "Accrington Magistrates' Court",
        "contacts": [
            {
                "sort": 2,
                "type": "Fax",
                "number": "0870 739 4254"
            },
            {
                "sort": 0,
                "type": "Enquiries",
                "number": "01254  687500"
            },
            {
                "sort": 1,
                "type": "Fine queries",
                "number": "01282  610000"
            },
            {
                "sort": 3,
                "type": "Witness service",
                "number": "01254 265 305"
            },
            {
                "sort": null,
                "type": "DX",
                "number": "742020 Blackburn 10"
            }
        ],
        "court_number": 1725,
        "lon": "-2.359323760375266",
        "postcodes": [],
        "areas_of_law": [
            {
                "councils": [],
                "name": "Crime"
            }
        ]
    },
"""
    self.countries
