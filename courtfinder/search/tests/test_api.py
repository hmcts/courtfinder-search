import requests
import json
import re
from django.test import TestCase, Client
from mock import Mock, patch
from search.court_search import CourtSearch, CourtSearchError, CourtSearchInvalidPostcode
from search.models import *
from django.conf import settings
from search.ingest import Ingest


class SearchTestCase(TestCase):

    def setUp(self):

        self.countries_json_1 = """[
    {
        "name": "England",
        "counties": [
            {
                "towns": [ "Accrington", "Blackburn", "Double Name", "Ashton-Under-Lyne" ],
                "name": "Lancashire"
            },
            {
                "towns": [ "Bedford", "Luton" ],
                "name": "Bedfordshire"
            }]}]
        """

        self.courts_json_1 = """[    {
        "addresses": [
            {
                "town": "Accrington",
                "type": "Visiting",
                "postcode": "BB5 2BH",
                "address": "East Lancashire Magistrates' Court\\nThe Law Courts\\nManchester Road"
            },
            {
                "town": "Blackburn",
                "type": "Postal",
                "postcode": "BB2 1AA",
                "address": "Accrington Magistrates' Court\\nThe Court House \\nNorthgate\\t\\n"
            }
        ],
        "admin_id": 2800,
        "facilities": [
            {
                "image_description": "Guide dogs icon.",
                "image": "guide_dogs",
                "description": "<p>Guide Dogs are welcome at this court.</p>\\r\\n",
                "name": "Guide dogs"
            },
            {
                "image_description": "Interview room icon.",
                "image": "interview",
                "description": "<p>Two interview rooms are available at this court.</p>\\r\\n",
                "name": "Interview room"
            },
            {
                "image_description": "Parking icon",
                "image": "parking",
                "description": "<p>There is free public parking at or nearby this court.</p>\\r\\n",
                "name": "Parking"
            },
            {
                "image_description": "Refreshments icon",
                "image": "hot_vending",
                "description": "<p>Refreshments are available.</p>\\r\\n",
                "name": "Refreshments"
            },
            {
                "image_description": "Disabled access icon",
                "image": "disabled",
                "description": "<p>This court has disabled toilet facilities, wheelchair access (assistance may be required from our staff) and a stairlift.</p>\\r\\n",
                "name": "Disabled access"
            },
            {
                "image_description": "Loop Hearing icon",
                "image": "loop_hearing",
                "description": "<p>This court has hearing enhancement facilities.</p>\\r\\n",
                "name": "Loop Hearing"
            },
            {
                "image_description": "Video facilities icon",
                "image": "video_conf",
                "description": "<p>Video conference and Prison Video Link facilities</p>\\r\\n",
                "name": "Video facilities"
            }
        ],
        "lat": "53.7491281247251",
        "slug": "accrington-magistrates-court",
        "opening_times": [
            "Court building open: Monday to Friday 9:15am to close of business"
        ],
        "court_types": [
            "Magistrates Court"
        ],
        "name": "Accrington Magistrates' Court",
        "contacts": [
            {
                "sort": 2,
                "name": "Fax",
                "number": "0870 739 4254"
            },
            {
                "sort": 0,
                "name": "Enquiries",
                "number": "01254  687500"
            },
            {
                "sort": 1,
                "name": "Fine queries",
                "number": "01282  610000"
            },
            {
                "sort": 3,
                "name": "Witness service",
                "number": "01254 265 305"
            },
            {
                "sort": null,
                "name": "DX",
                "number": "742020 Blackburn 10"
            }
        ],
        "court_number": 1725,
        "lon": "-2.359323760375266",
        "postcodes": ["SW1H9AJ"],
        "emails": [
            {
                "description": "Enquiries",
                "address": "ln-blackburnmcenq@hmcts.gsi.gov.uk"
            }
        ],
        "areas_of_law": [
            {
                "local_authorities": [],
                "name": "Crime"
            },
            {
                "local_authorities": [],
                "name": "Immigration"
            },
            {
                "local_authorities": [ "Southwark Borough Council" ],
                "name": "Divorce"
            }
        ],
        "image_file": "accrington_magistrates_court.jpg",
        "display": true
    },
    {
        "addresses": [
            {
                "town": "Ashton-Under-Lyne",
                "type": "Visiting",
                "postcode": "OL6 7TP",
                "address": "Henry Square\\n\\n\\n"
            }
        ],
        "admin_id": 2806,
        "facilities": [
            {
                "image_description": "Baby changing facility icon.",
                "image": "baby",
                "description": "<p>This Court has baby changing facilities.</p>\\r\\n",
                "name": "Baby changing facility"
            },
            {
                "image_description": "Guide dogs icon.",
                "image": "guide_dogs",
                "description": "<p>Guide Dogs are welcome at this Court.</p>\\r\\n",
                "name": "Guide dogs"
            },
            {
                "image_description": "Interview room icon.",
                "image": "interview",
                "description": "<p>This Court has interview room facilities.</p>\\r\\n",
                "name": "Interview room"
            },
            {
                "image_description": "Loop Hearing icon",
                "image": "loop_hearing",
                "description": "<p>This Court has hearing enhancement facilities.</p>\\r\\n",
                "name": "Loop Hearing"
            },
            {
                "image_description": "Parking icon",
                "image": "parking",
                "description": "<p>There is free public parking at or nearby this Court.</p>\\r\\n",
                "name": "Parking"
            },
            {
                "image_description": "Video facilities icon",
                "image": "video_conf",
                "description": "<p>Video conference and Prison Video Link facilities</p>\\r\\n",
                "name": "Video facilities"
            },
            {
                "image_description": "Refreshments icon",
                "image": "hot_vending",
                "description": "<p>Refreshments are available.</p>\\r\\n",
                "name": "Refreshments"
            },
            {
                "image_description": "Disabled access icon",
                "image": "disabled",
                "description": "<p>Disabled access, toilet and parking facilities.</p>\\r\\n",
                "name": "Disabled access"
            }
        ],
        "lat": "53.48557639318307",
        "slug": "tameside-magistrates-court",
        "opening_times": [
            "Court building open: 9.00 am to 5.00 pm",
            "Court counter open: 9.00 am to 4.00 pm",
            "Telephone Enquiries from: 9.00 am to 5.00 pm"
        ],
        "court_types": [
            "Magistrates Court"
        ],
        "name": "Tameside Magistrates' Court",
        "contacts": [
            {
                "sort": 0,
                "name": "Enquiries",
                "number": "0161  330 2023"
            },
            {
                "sort": 1,
                "name": "Enquiries",
                "number": "0161 331 5645"
            },
            {
                "sort": 3,
                "name": "Witness service",
                "number": "0161 339 9362"
            },
            {
                "sort": null,
                "name": "DX",
                "number": "702625 Ashton-under-Lyne 2"
            }
        ],
        "court_number": 1748,
        "lon": "-2.102120972524918",
        "postcodes": [],
        "emails": [
            {
                "description": "Enquiries",
                "address": "gm-tamesidemcadmin@hmcts.gsi.gov.uk"
            }
        ],
        "areas_of_law": [
            {
                "local_authorities": [],
                "name": "Crime"
            }
        ],
        "image_file": "tameside_magistrates_court.jpg",
        "display": true
    },
    {
        "name": "County Court Money Claims Centre (CCMCC)",
        "slug": "county-court-money-claims-centre-ccmcc",
        "lat": "1",
        "lon": "1",
        "admin_id": "3456543",
        "display": true,
        "court_number": "123456",
        "areas_of_law": [ { "local_authorities": [], "name": "Money claims" } ],
        "emails": [ { "description": "Enquiries", "address": "a@b.com" }],
        "attributes": [],
        "addresses": [],
        "court_types": [],
        "facilities": [],
        "opening_times": [],
        "contacts": [],
        "postcodes": []
    }
]"""

        Ingest.countries(json.loads(self.countries_json_1))
        Ingest.courts(json.loads(self.courts_json_1))


    def tearDown(self):
        pass


    def test_county(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertIn('"county": "Lancashire"', response.content)

    def test_postcode(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15+4UH&aol=Divorce')
        self.assertEqual(response.status_code, 200)

    def test_postcode_search(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15&aol=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

    def test_address_search(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

    def test_no_aol(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

    def test_empty_query(self):
        c = Client()
        response = c.get('/search/results.json?q=')
        self.assertEquals(400, response.status_code)

    def test_court_type(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertIn('Magistrates Court', response.content)
