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
                "towns": [ "Accrington", "Blackburn" ],
                "name": "Lancashire"
            },
            {
                "towns": [ "Bedford", "Luton" ],
                "name": "Bedfordshire"
            }]}]
        """

        self.courts_json_1 = """[{
        "addresses": [
            {
                "town": "Accrington",
                "type": "Visiting",
                "postcode": "BB5 2BH",
                "address": "East Lancashire Magistrates' Court\\nThe Law Courts\\nManchester Road\\n"
            },
            {
                "town": "Blackburn",
                "type": "Postal",
                "postcode": "BB2 1AA",
                "address": "Accrington Magistrates' Court\\nThe Court House \\nNorthgate"
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
        "postcodes": [ "CF335EE" ],
        "areas_of_law": [ { "councils": [], "name": "Money claims" }, { "councils": [ "Southwark Borough Council" ], "name": "Divorce" } ],
        "display": true
    }]"""

        Ingest.countries(json.loads(self.countries_json_1))
        Ingest.courts(json.loads(self.courts_json_1))

        def get_from_mapit_mock(url):
            matches = re.search('([^/]+)$', url)
            postcode = matches.group(0)
            if postcode == 'invalid':
                raise CourtSearchInvalidPostcode('Mapit doesn\'t know this postcode: '+url)
            elif len(postcode) < 4:
                return SearchTestCase.mock_mapit_partial
            else:
                return SearchTestCase.mock_mapit_full

        self.patcher =  patch('search.court_search.CourtSearch.get_from_mapit',
                              Mock(side_effect=get_from_mapit_mock))
        self.patcher.start()


    def tearDown(self):
        self.patcher.stop()


    def test_top_page_sans_slash_redirects_to_slash(self):
        c = Client()
        response = c.get('/search')
        self.assertRedirects(response, '/search/', 301)

    def test_search_type(self):
        c = Client()
        response = c.get('/search/type?type=postcode')
        self.assertRedirects(response, '/search/postcode', 302)

    def test_search_address(self):
        c = Client()
        response = c.get('/search/type?type=address')
        self.assertRedirects(response, '/search/address', 302)

    def test_search_list(self):
        c = Client()
        response = c.get('/search/type?type=list', follow=True)
        self.assertEqual(response.redirect_chain, [
            ('http://testserver/search/list', 302),
            ('https://courttribunalfinder.service.gov.uk/courts', 302)
        ])

    def test_format_results_with_postal_address(self):
        c = Client()
        response = c.get('/search/results?q=Accrington')
        self.assertIn("Blackburn", response.content)

    def test_search_space_in_name(self):
        c = Client()
        response = c.get('/search/results?q=Accrington+Magistrates')
        self.assertIn("Accrington", response.content)

    def test_postcode_civil_partnership(self):
        c = Client()
        response = c.get('/search/results?postcode=SE154UH&area_of_law=Civil+partnership', follow=True)
        self.assertIn("validation-error", response.content)

    def test_results_no_query(self):
        c = Client()
        response = c.get('/search/results?q=')
        self.assertRedirects(response, '/search/address?error=noquery', 302)

    def test_results_postcode_aol_not_selected(self):
        c = Client()
        response = c.get('/search/results?postcode=SE144EE&area_of_law=unselected')
        self.assertRedirects(response, '/search/postcode?postcode=SE144EE&area_of_law=', 302)

    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.jinja')
        self.assertInHTML('<title>Find a court or tribunal</title>', response.content, count=1)

    def test_sample_postcode_all_aols(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&area_of_law=All')
        self.assertEqual(response.status_code, 200)

    def test_sample_postcode_specific_aol(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&area_of_law=Divorce')
        self.assertEqual(response.status_code, 200)

    def test_sample_postcode_specific_aol2(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&area_of_law=Money+claims')
        self.assertEqual(response.status_code, 200)

    def test_sample_postcode_bad_aol(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&area_of_law=doesntexist', follow=True)
        self.assertIn('Sorry, your postcode', response.content)

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

    def test_regexp_city_should_match(self):
        c = Client()
        response = c.get('/search/results?q=accrington', follow=True)
        self.assertNotIn('validation-error', response.content)

    def test_scottish_postcodes(self):
        c = Client()
        response = c.get('/search/results?postcode=G24PP&area_of_law=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<p id="scotland">', response.content)
        response = c.get('/search/results?postcode=G2&area_of_law=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<p id="scotland">', response.content)
        response = c.get('/search/results?postcode=AB10&area_of_law=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<p id="scotland">', response.content)
        response = c.get('/search/results?postcode=AB10+7LY&area_of_law=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<p id="scotland">', response.content)
        response = c.get('/search/results?postcode=BA27AY&area_of_law=All')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<p id="scotland">', response.content)

    def test_partial_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15&area_of_law=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<div class="search-results">', response.content)

    def test_partial_postcode_whitespace(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15++&area_of_law=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<div class="search-results">', response.content)

    def test_postcode_whitespace(self):
        c = Client()
        response = c.get('/search/results?postcode=++SE154UH++&area_of_law=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<div class="search-results">', response.content)

    def test_unknown_directive_action(self):
        with patch('search.rules.Rules.for_postcode', Mock(return_value={'action':'blah2389'})):
            c = Client()
            response = c.get('/search/results?postcode=SE15')
            self.assertRedirects(response, '/search/', 302)

    def test_redirect_directive_action(self):
        with patch('search.rules.Rules.for_postcode', Mock(return_value={'action':'redirect', 'target':'postcode-view'})):
            c = Client()
            response = c.get('/search/results?postcode=BLARGH')
            self.assertRedirects(response, '/search/postcode', 302)

    def test_redirect_directive_action_json(self):
        with patch('search.rules.Rules.for_postcode',
                   Mock(return_value={'action':'redirect', 'target':'http://www.example.org'})):
            c = Client()
            response = c.get('/search/results.json?postcode=SE15&area_of_law=Divorce')
            self.assertEquals(400, response.status_code)

    def test_county_in_json(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertIn('"county": "Lancashire"', response.content)

    def test_empty_query_json(self):
        c = Client()
        response = c.get('/search/results.json?q=')
        self.assertEquals(400, response.status_code)

    def test_court_type_in_json(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertIn('Magistrates Court', response.content)

    def test_no_aol_json(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15')
        self.assertEqual(response.status_code, 400)

    def test_json_postcode_search(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15&area_of_law=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)

    def test_json_name_search(self):
        c = Client()
        response = c.get('/search/results.json?q=Accrington')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "Accrington Magistrates\' Court"', response.content)


    def test_api_broken_mapit(self):
        with patch('search.court_search.CourtSearch.get_from_mapit', Mock(side_effect=CourtSearchError('Mapit error'))):
            with self.assertRaises(CourtSearchError):
                c = Client()
                response = c.get('/search/results.json?postcode=SE154UH&area_of_law=Crime')
                self.assertEqual(response.status_code, 500)


    def test_search_no_postcode_nor_q(self):
        c = Client()
        response = c.get('/search/results')
        self.assertRedirects(response, '/search/', 302)

    def test_api_postcode(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15+4UH&area_of_law=Divorce')
        self.assertEqual(response.status_code, 200)

    def test_postcode_to_local_authority_short_postcode(self):
        self.assertEqual(len(CourtSearch.local_authority_search('SE15', 'Divorce')), 1)

    def test_bad_local_authority(self):
        with patch('search.court_search.CourtSearch.postcode_to_local_authority', Mock(return_value="local authority name that does not exist")):
            self.assertEqual(CourtSearch.local_authority_search('SE154UH', 'Money claims'), [])

    def test_broken_postcode_to_latlon(self):
        with patch('search.court_search.CourtSearch.postcode_to_latlon', Mock(side_effect=Exception('something went wrong'))):
            with self.assertRaises(Exception):
                CourtSearch.proximity_search('SE154UH', 'Money claims')

    def test_proximity_search(self):
        self.assertNotEqual(CourtSearch.proximity_search('SE154UH', 'Divorce'), [])

    def test_address_search(self):
        c = Client()
        response = c.get('/search/results?q=Road')
        self.assertEqual(response.status_code, 200)

    def test_broken_postcode_latlon_mapping(self):
        self.assertEqual(CourtSearch.postcode_search('Z', 'all'), [])


    def test_broken_mapit(self):
        with patch('search.court_search.CourtSearch.get_from_mapit', Mock(side_effect=CourtSearchError('Mapit error'))):
            with self.assertRaises(CourtSearchError):
                c = Client()
                response = c.get('/search/results?postcode=SE154UH')
                self.assertEqual(response.status_code, 500)

    def test_postcode_search(self):
        self.assertNotEqual(CourtSearch.postcode_search('CF335EE', 'all'), [])

    def test_empty_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=')
        self.assertEqual(response.status_code, 302)

    def test_ni_immigration(self):
        glasgow = Court.objects.create(
            name="Glasgow Tribunal Hearing Centre",
            lat=0.0,
            lon=0.0,
        )
        c = Client()
        response = c.get('/search/results?postcode=bt2&area_of_law=Immigration')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Glasgow Tribunal Hearing Centre", response.content)

    def test_ni(self):
        c = Client()
        response = c.get('/search/results?postcode=bt2&area_of_law=Divorce', follow=True)
        self.assertIn("this tool does not return results for Northern Ireland", response.content)

    def test_court_postcodes(self):
        court = Court.objects.get(name="Accrington Magistrates' Court")
        self.assertEqual(len(court.postcodes_covered()), 1)

    def test_court_local_authority_aol_covered(self):
        court = Court.objects.get(name="Accrington Magistrates' Court")
        aol = AreaOfLaw.objects.get(name="Divorce")
        court_aol = CourtAreasOfLaw.objects.get(court=court, area_of_law=aol)
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
        aols = CourtAreasOfLaw.objects.create(court=court, area_of_law=aol)
        self.assertEqual(str(aols), "Accrington Magistrates' Court deals with Divorce")
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
        contact_type = ContactType.objects.create(name="email")
        self.assertEqual(str(contact_type), "email")
        court_type = CourtType.objects.create(name="crown court")
        self.assertEqual(str(court_type), "crown court")
        court_contact = CourtContact.objects.create(contact_type=contact_type,
                                                    court=court,
                                                    value="a@b.com")
        self.assertEqual(str(court_contact), "email for Accrington Magistrates' Court is a@b.com")
        court_court_types=CourtCourtTypes.objects.create(court=court,
                                                        court_type=court_type)
        self.assertEqual(str(court_court_types), "Court type for Accrington Magistrates' Court is crown court")
        court_postcodes=CourtPostcodes.objects.create(court=court,
                                                      postcode="BR27AY")
        self.assertEqual(str(court_postcodes), "Accrington Magistrates' Court covers BR27AY")
        local_authority=LocalAuthority.objects.create(name="Southwark Borough Council")
        self.assertEqual(str(local_authority), "Southwark Borough Council")
        court_local_authority_aol=CourtLocalAuthorityAreaOfLaw(court=court,
                                                               area_of_law=aol,
                                                               local_authority=local_authority)
        self.assertEqual(str(court_local_authority_aol), "Accrington Magistrates' Court covers Southwark Borough Council for Divorce")

    def test_broken_mapit(self):
        # we need to stop the patched mapit method to run the original version, but with a borken URL
        self.patcher.stop()
        saved = settings.MAPIT_BASE_URL
        settings.MAPIT_BASE_URL = 'http://example.com/'
        with self.assertRaises(Exception):
            CourtSearch.postcode_to_latlon('SE144UR')
        settings.MAPIT_BASE_URL = saved
        self.patcher.start()

    def test_if_mapit_works(self):
        # we need to stop the patched mapit method to run the real mapit service
        self.patcher.stop()
        CourtSearch.get_full_postcode('SE154UH')
        CourtSearch.get_partial_postcode('SE15')
        self.patcher.start()

    def test_invalid_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=INVALID&area_of_law=All')
        self.assertRedirects(response, '/search/postcode?error=badpc&postcode=INVALID')

    def test_mapit_doesnt_return_correct_data(self):
        # we need to stop the patched mapit method to run a mock returning bad content
        self.patcher.stop()
        with patch('search.court_search.CourtSearch.get_from_mapit', Mock(return_value="garbage")):
            with self.assertRaises(Exception):
                CourtSearch.postcode_to_latlon('SE154UH')
        self.patcher.start()


    def test_local_authority_search_bad_aol(self):
        self.assertEquals(CourtSearch.local_authority_search('SE154UH', 'non-existent-aol'), [])

    mock_mapit_partial = '{"wgs84_lat": 51.47263752259685, "coordsyst": "G", "wgs84_lon": -0.06603088421009512, "postcode": "SE15", "easting": 534416, "northing": 176632}'

    mock_mapit_full = '{"wgs84_lat": 51.468945906164286, "coordsyst": "G", "shortcuts": {"WMC": 65913, "ward": 8328, "council": 2491}, "wgs84_lon": -0.06623508303668792, "postcode": "SE15 4UH", "easting": 534412, "areas": {"900000": {"parent_area": null, "generation_high": 19, "all_names": {}, "id": 900000, "codes": {}, "name": "House of Commons", "country": "", "type_name": "UK Parliament", "generation_low": 1, "country_name": "-", "type": "WMP"}, "900001": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 900001, "codes": {}, "name": "European Parliament", "country": "", "type_name": "European Parliament", "generation_low": 1, "country_name": "-", "type": "EUP"}, "900002": {"parent_area": 900006, "generation_high": 22, "all_names": {}, "id": 900002, "codes": {}, "name": "London Assembly", "country": "E", "type_name": "London Assembly area (shared)", "generation_low": 1, "country_name": "England", "type": "LAE"}, "2491": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 2491, "codes": {"ons": "00BE", "gss": "E09000028", "unit_id": "11013"}, "name": "Southwark Borough Council", "country": "E", "type_name": "London borough", "generation_low": 1, "country_name": "England", "type": "LBO"}, "104581": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 104581, "codes": {"ons": "E01004062"}, "name": "Southwark 025B", "country": "E", "type_name": "Lower Layer Super Output Area (Generalised)", "generation_low": 13, "country_name": "England", "type": "OLG"}, "900006": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 900006, "codes": {}, "name": "London Assembly", "country": "E", "type_name": "London Assembly area", "generation_low": 1, "country_name": "England", "type": "LAS"}, "2247": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 2247, "codes": {"unit_id": "41441"}, "name": "Greater London Authority", "country": "E", "type_name": "Greater London Authority", "generation_low": 1, "country_name": "England", "type": "GLA"}, "8328": {"parent_area": 2491, "generation_high": 22, "all_names": {}, "id": 8328, "codes": {"ons": "00BEGY", "gss": "E05000553", "unit_id": "11051"}, "name": "The Lane", "country": "E", "type_name": "London borough ward", "generation_low": 1, "country_name": "England", "type": "LBW"}, "11822": {"parent_area": 2247, "generation_high": 22, "all_names": {}, "id": 11822, "codes": {"gss": "E32000010", "unit_id": "41446"}, "name": "Lambeth and Southwark", "country": "E", "type_name": "London Assembly constituency", "generation_low": 1, "country_name": "England", "type": "LAC"}, "41904": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 41904, "codes": {"ons": "E02000831"}, "name": "Southwark 025", "country": "E", "type_name": "Middle Layer Super Output Area (Generalised)", "generation_low": 13, "country_name": "England", "type": "OMG"}, "34710": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 34710, "codes": {"ons": "E02000831"}, "name": "Southwark 025", "country": "E", "type_name": "Middle Layer Super Output Area (Full)", "generation_low": 13, "country_name": "England", "type": "OMF"}, "65913": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 65913, "codes": {"gss": "E14000615", "unit_id": "25066"}, "name": "Camberwell and Peckham", "country": "E", "type_name": "UK Parliament constituency", "generation_low": 13, "country_name": "England", "type": "WMC"}, "70203": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 70203, "codes": {"ons": "E01004062"}, "name": "Southwark 025B", "country": "E", "type_name": "Lower Layer Super Output Area (Full)", "generation_low": 13, "country_name": "England", "type": "OLF"}, "11806": {"parent_area": null, "generation_high": 22, "all_names": {}, "id": 11806, "codes": {"ons": "07", "gss": "E15000007", "unit_id": "41428"}, "name": "London", "country": "E", "type_name": "European region", "generation_low": 1, "country_name": "England", "type": "EUR"}}, "northing": 176221}'
