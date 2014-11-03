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

    def test_format_results_with_postal_address(self):
        c = Client()
        response = c.get('/search/results?q=Accrington')
        self.assertIn("Blackburn", response.content)

    def test_format_results_with_empty_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=')
        self.assertRedirects(response, '/search/', 302)

    def test_search_space_in_name(self):
        c = Client()
        response = c.get('/search/results?q=Accrington+Magistrates')
        self.assertIn("Accrington", response.content)

    def test_aol_page(self):
        c = Client()
        response = c.get('/search/aol')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/aol.jinja')
        self.assertIn('About your issue', response.content)

    def test_spoe_page_with_has_spoe(self):
        c = Client()
        response = c.get('/search/spoe?aol=Children')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/spoe.jinja')
        self.assertIn('About your issue', response.content)

    def test_spoe_page_without_spoe(self):
        c = Client()
        response = c.get('/search/spoe?aol=Crime', follow=True)
        self.assertInHTML('<h1>Enter postcode</h1>', response.content)


#    def test_postcode_civil_partnership(self):
#        c = Client()
#        response = c.get('/search/results?postcode=SE154UH&aol=Civil+partnership', follow=True)
#        self.assertIn("validation-error", response.content)

    def test_results_no_query(self):
        c = Client()
        response = c.get('/search/results?q=')
        self.assertRedirects(response, '/search/address?error=noquery', 302)

#    def test_sample_postcode_all_aols(self):
#        c = Client()
#        response = c.get('/search/results?postcode=SE15+4UH&aol=All')
#        self.assertEqual(response.status_code, 200)

#    def test_sample_postcode_specific_aol(self):
#        c = Client()
#        response = c.get('/search/results?postcode=SE15+4UH&aol=Divorce')
#        self.assertEqual(response.status_code, 200)
#
#    def test_sample_postcode_specific_aol2(self):
#        c = Client()
#        response = c.get('/search/results?postcode=SE15+4UH&aol=Divorce')
#        self.assertEqual(response.status_code, 200)

#    def test_sample_postcode_bad_aol(self):
#        c = Client()
#        response = c.get('/search/results?postcode=SE15+4UH&aol=doesntexist', follow=True)
#        self.assertIn('Sorry, your postcode', response.content)

    def test_inactive_court(self):
        court = Court.objects.create(
            name="Example2 Court",
            lat=0.0,
            lon=0.0,
            displayed=False,
        )
        c = Client()
        response = c.get('/search/results?q=Example2+Court', follow=True)
        self.assertIn('validation-error', response.content)

    def test_substring_should_not_match(self):
        c = Client()
        response = c.get('/search/results?q=ample2', follow=True)
        self.assertIn('validation-error', response.content)

    def test_too_much_whitespace_in_address_search(self):
        c = Client()
        response = c.get('/search/results?q=Accrington++++Magistrates', follow=True)
        self.assertNotIn('validation-error', response.content)

    def test_regexp_city_should_match(self):
        c = Client()
        response = c.get('/search/results?q=accrington', follow=True)
        self.assertNotIn('validation-error', response.content)

    def test_scottish_postcodes(self):
        c = Client()
        response = c.get('/search/results?postcode=G24PP&aol=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<p id="scotland">', response.content)
        response = c.get('/search/results?postcode=G2&aol=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<p id="scotland">', response.content)
        response = c.get('/search/results?postcode=AB10&aol=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<p id="scotland">', response.content)
        response = c.get('/search/results?postcode=AB10+7LY&aol=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<p id="scotland">', response.content)
        response = c.get('/search/results?postcode=BA27AY&aol=All')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<p id="scotland">', response.content)

#    def test_partial_postcode(self):
#        c = Client()
#        response = c.get('/search/results?postcode=SE15&aol=All')
#        self.assertEqual(response.status_code, 200)
#        self.assertIn('<div class="search-results">', response.content)

#    def test_partial_postcode_whitespace(self):
#        c = Client()
#        response = c.get('/search/results?postcode=SE15++&aol=All')
#        self.assertEqual(response.status_code, 200)
#        self.assertIn('<div class="search-results">', response.content)

#    def test_postcode_whitespace(self):
#        c = Client()
#        response = c.get('/search/results?postcode=++SE154UH++&aol=All')
#        self.assertEqual(response.status_code, 200)
#        self.assertIn('<div class="search-results">', response.content)

#    def test_unknown_directive_action(self):
#        with patch('search.rules.Rules.for_postcode', Mock(return_value={'action':'blah2389'})):
#            c = Client()
#            response = c.get('/search/results?postcode=SE15')
#            self.assertRedirects(response, '/search/', 302)

#    def test_redirect_directive_action(self):
#        with patch('search.rules.Rules.for_postcode', Mock(return_value={'action':'redirect', 'target':'postcode-view'})):
#            c = Client()
#            response = c.get('/search/results?postcode=BLARGH')
#            self.assertRedirects(response, '/search/postcode', 302)

#    def test_redirect_directive_action_json(self):
#        with patch('search.rules.Rules.for_postcode',
#                   Mock(return_value={'action':'redirect', 'target':'http://www.example.org'})):
#            c = Client()
#            response = c.get('/search/results.json?postcode=SE15&aol=Divorce')
#            self.assertEquals(400, response.status_code)

#    def test_county_in_json(self):
#        c = Client()
#        response = c.get('/search/results.json?q=Accrington')
#        self.assertIn('"county": "Lancashire"', response.content)

    def test_empty_query_json(self):
        c = Client()
        response = c.get('/search/results.json?q=')
        self.assertEquals(400, response.status_code)

#    def test_court_type_in_json(self):
#        c = Client()
#        response = c.get('/search/results.json?q=Accrington')
#        self.assertIn('Magistrates Court', response.content)

    def test_no_aol_json(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15')
        self.assertEqual(response.status_code, 400)

#    def test_json_postcode_search(self):
#        c = Client()
#        response = c.get('/search/results.json?postcode=SE15&aol=Divorce')
#        self.assertEqual(response.status_code, 200)
#        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

#    def test_json_name_search(self):
#        c = Client()
#        response = c.get('/search/results.json?q=Accrington')
#        self.assertEqual(response.status_code, 200)
#        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

#    def test_api_broken_mapit_with_name_search(self):
#        with patch('search.court_search.CourtSearch.address_search', Mock(side_effect=CourtSearchError('Service Error'))):
#            c = Client()
#            response = c.get('/search/results.json?q=old+bailey')
#            self.assertEqual(response.status_code, 500)

#    def test_api_broken_mapit_with_postcode_search(self):
#        with patch('search.court_search.CourtSearch.get_from_mapit', Mock(side_effect=CourtSearchError('Mapit error'))):
#            with self.assertRaises(CourtSearchError):
#                c = Client()
#                response = c.get('/search/results.json?postcode=SE154UH&aol=Crime')
#                self.assertEqual(response.status_code, 500)

    def test_search_no_postcode_nor_q(self):
        c = Client()
        response = c.get('/search/results')
        self.assertRedirects(response, '/search/', 302)

#    def test_api_postcode(self):
#        c = Client()
#        response = c.get('/search/results.json?postcode=SE15+4UH&aol=Divorce')
#        self.assertEqual(response.status_code, 200)

#    def test_postcode_to_local_authority_short_postcode(self):
#        self.assertEqual(len(CourtSearch.local_authority_search('SE15', 'Divorce')), 1)

#    def test_local_authority_search_ordered(self):
#        self.assertEqual(CourtSearch.local_authority_search('SE15 4UH', 'Divorce')[0].name, "Accrington Magistrates' Court")

#    def test_bad_local_authority(self):
#        with patch('search.court_search.CourtSearch.postcode_to_local_authority', Mock(return_value="local authority name that does not exist")):
#            self.assertEqual(CourtSearch.local_authority_search('SE154UH', 'Money claims'), [])

#    def test_broken_postcode_to_latlon(self):
#        with patch('search.court_search.CourtSearch.postcode_to_latlon', Mock(side_effect=Exception('something went wrong'))):
#            with self.assertRaises(Exception):
#                CourtSearch.proximity_search('SE154UH', 'Money claims')

#    def test_proximity_search(self):
#        self.assertNotEqual(CourtSearch.proximity_search('SE154UH', 'Divorce'), [])

    def test_address_search(self):
        c = Client()
        response = c.get('/search/results?q=Road')
        self.assertEqual(response.status_code, 200)

    def test_partial_word_match(self):
        c = Client()
        response = c.get('/search/results?q=accrington+court')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Accrington Magistrates', response.content)

    def test_unordered_word_match(self):
        c = Client()
        response = c.get('/search/results?q=magistrates+court+accrington')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Accrington Magistrates', response.content)

#    def test_broken_postcode_latlon_mapping(self):
#        self.assertEqual(CourtSearch.postcode_search('Z', 'all'), [])


#    def test_broken_mapit(self):
#        with patch('search.court_search.CourtSearch.get_from_mapit', Mock(side_effect=CourtSearchError('Mapit error'))):
#            with self.assertRaises(CourtSearchError):
#                c = Client()
#                response = c.get('/search/results?postcode=SE154UH')
#                self.assertEqual(response.status_code, 500)

#    def test_postcode_search(self):
#        self.assertNotEqual(CourtSearch.postcode_search('SW1H9AJ', 'all'), [])

    def test_empty_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=')
        self.assertEqual(response.status_code, 302)

#    def test_ni_immigration(self):
#        glasgow = Court.objects.create(
#            name="Glasgow Tribunal Hearing Centre",
#            slug="something",
#            lat=0.0,
#            lon=0.0,
#        )
#        c = Client()
#        response = c.get('/search/results?postcode=bt2&aol=Immigration')
#        self.assertEqual(response.status_code, 200)
#        self.assertIn("Glasgow Tribunal Hearing Centre", response.content)

    def test_ni(self):
        c = Client()
        response = c.get('/search/results?postcode=bt2&aol=Divorce', follow=True)
        self.assertIn("this tool does not return results for Northern Ireland", response.content)

    def test_money_claims(self):
        c = Client()
        response = c.get('/search/results?postcode=sw1h9aj&aol=Money+claims')
        self.assertIn("CCMCC", response.content)

    def test_ni_immigration(self):
        c = Client()
        response = c.get('/search/results?postcode=bt2&aol=Immigration', follow=True)
        self.assertNotIn("this tool does not return results for Northern Ireland", response.content)

    def test_court_postcodes(self):
        court = Court.objects.get(name="Accrington Magistrates' Court")
        self.assertEqual(len(court.postcodes_covered()), 1)

    def test_court_local_authority_aol_covered(self):
        court = Court.objects.get(name="Accrington Magistrates' Court")
        aol = AreaOfLaw.objects.get(name="Divorce")
        court_aol = CourtAreaOfLaw.objects.get(court=court, area_of_law=aol)
        self.assertEqual(len(court_aol.local_authorities_covered()), 1)
        self.assertEqual(str(court_aol.local_authorities_covered()[0]),
                         "Accrington Magistrates' Court covers Southwark Borough Council for Divorce")

    def test_models_unicode(self):
        court = Court.objects.get(name="Accrington Magistrates' Court")
        self.assertEqual(str(court), "Accrington Magistrates' Court")
        cat = CourtAttributeType.objects.create(name="cat")
        self.assertEqual(str(cat), "cat")
        ca = CourtAttribute.objects.create(court=court, attribute_type=cat, value="cav")
        self.assertEqual(str(ca), "Accrington Magistrates' Court.cat = cav")
        aol = AreaOfLaw.objects.create(name="Divorce")
        self.assertEqual(str(aol), "Divorce")
        aols = CourtAreaOfLaw.objects.create(court=court, area_of_law=aol)
        self.assertEqual(str(aols), "Accrington Magistrates' Court deals with Divorce (spoe: False)")
        country = Country.objects.create(name="Wales")
        self.assertEqual(str(country), "Wales")
        county = County.objects.create(name="Shire", country=country)
        self.assertEqual(str(county), "Shire")
        town = Town.objects.create(name="Hobbittown", county=county)
        self.assertEqual(str(town), "Hobbittown")
        address_type = AddressType.objects.create(name="Postal")
        self.assertEqual(str(address_type), "Postal")
        court_address = CourtAddress.objects.create(address_type=address_type,
                                                    court=court,
                                                    address="The court address",
                                                    postcode="CF34RR",
                                                    town=town)
        self.assertEqual(str(court_address), "Postal for Accrington Magistrates' Court is The court address, CF34RR, Hobbittown")
        contact = Contact.objects.create(name="Enquiries", number="0123456789")
        self.assertEqual(str(contact), "Enquiries: 0123456789")
        court_type = CourtType.objects.create(name="crown court")
        self.assertEqual(str(court_type), "crown court")
        court_contact = CourtContact.objects.create(contact=contact, court=court)
        self.assertEqual(str(court_contact), "Enquiries for Accrington Magistrates' Court is 0123456789")
        court_court_types=CourtCourtType.objects.create(court=court,
                                                        court_type=court_type)
        self.assertEqual(str(court_court_types), "Court type for Accrington Magistrates' Court is crown court")
        court_postcodes=CourtPostcode.objects.create(court=court,
                                                      postcode="BR27AY")
        self.assertEqual(str(court_postcodes), "Accrington Magistrates' Court covers BR27AY")
        local_authority=LocalAuthority.objects.create(name="Southwark Borough Council")
        self.assertEqual(str(local_authority), "Southwark Borough Council")
        court_local_authority_aol=CourtLocalAuthorityAreaOfLaw(court=court,
                                                               area_of_law=aol,
                                                               local_authority=local_authority)
        self.assertEqual(str(court_local_authority_aol), "Accrington Magistrates' Court covers Southwark Borough Council for Divorce")
        facility=Facility.objects.create(name="sofa", description="comfy leather")
        self.assertEqual(str(facility), "sofa: comfy leather")
        court_facility = CourtFacility.objects.create(court=court, facility=facility)
        self.assertEqual(str(court_facility), "%s has facility %s" % (court.name, facility))
        opening_time = OpeningTime.objects.create(description="open 7/7")
        self.assertEqual(str(opening_time), "open 7/7")
        court_opening_time = CourtOpeningTime.objects.create(court=court, opening_time=opening_time)
        self.assertEqual(str(court_opening_time), "%s has facility %s" % (court.name, opening_time))
        email = Email.objects.create(description="enquiries", address="a@b.com")
        self.assertEqual(str(email), "enquiries: a@b.com")
        court_email = CourtEmail.objects.create(court=court, email=email)
        self.assertEqual(str(court_email), "%s has email: %s" % (court.name, email.description))
        now = datetime.now()
        data_status = DataStatus.objects.create(data_hash="wer38hr3hr37hr")
        self.assertEqual(str(data_status), "Current data hash: %s, last update: %s" %
                         (data_status.data_hash, data_status.last_ingestion_date))
        parking_info = ParkingInfo.objects.create(onsite="foo", offsite="bar", blue_badge="baz")
        self.assertEqual(str(parking_info), "Parking onsite: foo, Parking offsite: bar, Parking blue-badge: baz")

#    def test_broken_mapit(self):
#        # we need to stop the patched mapit method to run the original version, but with a borken URL
#        self.patcher.stop()
#        saved = settings.MAPIT_BASE_URL
#        settings.MAPIT_BASE_URL = 'http://example.com/'
#        with self.assertRaises(Exception):
#            CourtSearch.postcode_to_latlon('SE144UR')
#        settings.MAPIT_BASE_URL = saved
#        self.patcher.start()
#
#    def test_if_mapit_works(self):
#        # we need to stop the patched mapit method to run the real mapit service
#        self.patcher.stop()
#        CourtSearch.get_full_postcode('SE154UH')
#        CourtSearch.get_partial_postcode('SE15')
#        self.patcher.start()
#
#    def test_invalid_postcode(self):
#        c = Client()
#        response = c.get('/search/results?postcode=INVALID&aol=All')
#        self.assertRedirects(response, '/search/postcode?error=badpc&postcode=INVALID')

#    def test_mapit_doesnt_return_correct_data(self):
#        # we need to stop the patched mapit method to run a mock returning bad content
#        self.patcher.stop()
#        with patch('search.court_search.CourtSearch.get_from_mapit', Mock(return_value="garbage")):
#            with self.assertRaises(Exception):
#                CourtSearch.postcode_to_latlon('SE154UH')
#        self.patcher.start()

#    def test_local_authority_search_bad_aol(self):
#        self.assertEquals(CourtSearch.local_authority_search('SE154UH', 'non-existent-aol'), [])
