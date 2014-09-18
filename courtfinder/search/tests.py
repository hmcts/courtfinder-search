from django.test import TestCase, Client
import requests
from mock import Mock, patch
from search.court_search import CourtSearch
from search.models import *
from django.conf import settings


class SearchTestCase(TestCase):

    def setUp(self):
        self.court = Court.objects.create(
            name="Example Court",
            lat=0.0,
            lon=0.0,
        )
        self.address_type = AddressType.objects.create(name='Postal')
        self.country = Country.objects.create(name='Wales')
        self.county = County.objects.create(name='Shire', country=self.country)
        self.town = Town.objects.create(name='Hobbittown', county=self.county)
        self.court_address = CourtAddress.objects.create(
            address_type=self.address_type,
            court=self.court,
            address='The court address',
            postcode='CF34RR',
            town=self.town,
        )
        self.area_of_law = AreaOfLaw.objects.create(name="crimes")
        self.court_areas_of_law = CourtAreasOfLaw.objects.create(
            court=self.court,
            area_of_law=self.area_of_law,
        )
        self.court_postcodes = CourtPostcodes.objects.create(court=self.court, postcode='CF335EE')
        self.local_authority = LocalAuthority.objects.create(name='Meh council')
        self.court_local_authority_area_of_law = CourtLocalAuthorityAreaOfLaw(
            court=self.court,
            area_of_law=self.area_of_law,
            local_authority=self.local_authority,
        )
        self.court_attribute_type = CourtAttributeType.objects.create(name="cat")
        self.court_attribute = CourtAttribute.objects.create(
            court=self.court,
            attribute_type=self.court_attribute_type,
            value="cav"
        )
        self.contact_type = ContactType.objects.create(name="email")
        self.court_type = CourtType.objects.create(name="crown court")
        self.court_court_type = CourtCourtTypes(
            court=self.court,
            court_type=self.court_type,
        )
        self.court_contact = CourtContact.objects.create(
            contact_type=self.contact_type,
            court=self.court,
            value="a@b.com"
        )

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
        response = c.get('/search/results?q=Example')
        self.assertIn("Hobbittown", response.content)

    def test_results_no_query(self):
        c = Client()
        response = c.get('/search/results?q=')
        self.assertRedirects(response, '/search/address?error=1', 302)

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

    def test_sample_postcode_bad_aol(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&area_of_law=doesntexist')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sorry, there are no results', response.content)

    def test_partial_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15&area_of_law=All')
        self.assertEqual(response.status_code, 200)

    def test_unknown_directive_action(self):
        with patch('search.rules.Rules.for_postcode', Mock(return_value={'action':'blah2389'})):
            c = Client()
            response = c.get('/search/results?postcode=SE15')
            self.assertRedirects(response, '/search/', 302)

    def test_redirect_directive_action(self):
        with patch('search.rules.Rules.for_postcode', Mock(return_value={'action':'redirect', 'target':'http://www.example.org'})):
            c = Client()
            response = c.get('/search/results?postcode=SE15')
            self.assertRedirects(response, 'http://www.example.org', 302)

    def test_redirect_directive_action_json(self):
        with patch('search.rules.Rules.for_postcode', Mock(return_value={'action':'redirect', 'target':'http://www.example.org'})):
            c = Client()
            response = c.get('/search/results.json?postcode=SE15&area_of_law=Divorce')
            self.assertRedirects(response, 'http://www.example.org', 302)

    def test_no_aol_json(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15')
        self.assertEqual(response.status_code, 200)
        self.assertIn('{}', response.content)

    def test_search_no_postcode_nor_q(self):
        c = Client()
        response = c.get('/search/results')
        self.assertRedirects(response, '/search/', 302)

    def test_api_postcode(self):
        c = Client()
        response = c.get('/search/results.json?postcode=SE15+4UH&area_of_law=Bankruptcy')
        self.assertEqual(response.status_code, 200)

    def test_postcode_to_local_authority_short_postcode(self):
        self.assertEqual(CourtSearch.local_authority_search('SE15', 'Divorce'), [])

    def test_mapit_returns_county_in_councils(self):
        with patch('search.court_search.CourtSearch.get_from_mapit',
                   Mock(return_value='{"shortcuts":{"council":{"county":"meh"}},"areas":{"meh":{"name":"some name"}}}')):
            self.assertEqual(CourtSearch.postcode_to_local_authority('SE154EE', 'all'), "some name")

    def test_bad_local_authority(self):
        with patch('search.court_search.CourtSearch.postcode_to_local_authority', Mock(return_value="local authority name that does not exist")):
            self.assertEqual(CourtSearch.local_authority_search('SE154UH', 'Money claims'), [])

    def test_broken_postcode_to_latlon(self):
        with patch('search.court_search.CourtSearch.postcode_to_latlon', Mock(side_effect=Exception('something went wrong'))):
            self.assertEqual(CourtSearch.proximity_search('SE154UH', 'Money claims'), [])

    def test_proximity_search(self):
        self.assertNotEqual(CourtSearch.proximity_search('SE154UH', 'crimes'), [])

    def test_address_search(self):
        c = Client()
        response = c.get('/search/results?q=Leeds')
        self.assertEqual(response.status_code, 200)

    def test_broken_postcode_latlon_mapping(self):
        self.assertEqual(CourtSearch.postcode_search('Z', 'all'), [])

    def test_broken_mapit(self):
        saved = settings.MAPIT_BASE_URL
        settings.MAPIT_BASE_URL = 'http://broken.example.com/'
        with self.assertRaises(requests.exceptions.ConnectionError):
            CourtSearch.postcode_to_latlon('SE144UR')
        settings.MAPIT_BASE_URL = saved

    def test_broken_mapit_2(self):
        with self.assertRaises(Exception):
            CourtSearch.get_from_mapit("http://localhost/this_should_always_return_404")

    def test_mapit_doesnt_return_correct_data(self):
        with patch('search.court_search.CourtSearch.get_from_mapit', Mock(return_value="garbage")):
            with self.assertRaises(Exception):
                CourtSearch.postcode_to_latlon('SE154UH')

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
        response = c.get('/search/results?postcode=bt2&area_of_law=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertIn("this tool does not return results for Northern Ireland", response.content)

    def test_court_postcodes(self):
        self.assertEqual(len(self.court.postcodes_covered()), 1)

    def test_court_local_authority_aol_covered(self):
        self.assertEqual(len(self.court_areas_of_law.local_authorities_covered()), 0)

    def test_models_unicode(self):
        self.assertEqual(str(self.court), "Example Court")
        self.assertEqual(str(self.court_attribute_type), "cat")
        self.assertEqual(str(self.court_attribute), "Example Court.cat = cav")
        self.assertEqual(str(self.area_of_law), "crimes")
        self.assertEqual(str(self.court_areas_of_law), "Example Court deals with crimes")
        self.assertEqual(str(self.country), "Wales")
        self.assertEqual(str(self.county), "Shire")
        self.assertEqual(str(self.town), "Hobbittown")
        self.assertEqual(str(self.address_type), "Postal")
        self.assertEqual(str(self.court_address), "Postal for Example Court is The court address, CF34RR, Hobbittown")
        self.assertEqual(str(self.contact_type), "email")
        self.assertEqual(str(self.court_type), "crown court")
        self.assertEqual(str(self.court_contact), "email for Example Court is a@b.com")
        self.assertEqual(str(self.court_court_type), "Court type for Example Court is crown court")
        self.assertEqual(str(self.court_postcodes), "Example Court covers CF335EE")
        self.assertEqual(str(self.local_authority), "Meh council")
        self.assertEqual(str(self.court_local_authority_area_of_law), "Example Court covers Meh council for crimes")
