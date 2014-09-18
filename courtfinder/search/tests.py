from django.test import TestCase, Client
import requests
from mock import Mock, patch
from search.court_search import CourtSearch
from search.models import *
from django.conf import settings


class SearchTestCase(TestCase):

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
        self.assertIn("Northgate", response.content)

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
        self.assertNotEqual(CourtSearch.proximity_search('SE154UH', 'Money claims'), [])

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
        self.assertNotEqual(CourtSearch.postcode_search('SE154UH', 'all'), [])

    def test_empty_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=')
        self.assertEqual(response.status_code, 302)

    def test_ni_immigration(self):
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
        c = Court.objects.get(name="Bedford County Court and Family Court")
        self.assertEqual(len(c.postcodes_covered()), 97)

    def test_court_local_authority_aol_covered(self):
        c = Court.objects.get(name='Barnet Civil and Family Courts Centre')
        aol = AreaOfLaw.objects.get(name='Children')
        ca = CourtAreasOfLaw.objects.create(court=c, area_of_law=aol)
        self.assertEqual(len(ca.local_authorities_covered()), 4)

    def test_models_unicode(self):
        c = Court.objects.get(name="Accrington Magistrates' Court")
        self.assertEqual(str(c), "Accrington Magistrates' Court")
        cat = CourtAttributeType.objects.create(name="cat")
        self.assertEqual(str(cat), "cat")
        ca = CourtAttribute.objects.create(court=c, attribute_type=cat, value="cav")
        self.assertEqual(str(ca), "Accrington Magistrates' Court.cat = cav")
        aol = AreaOfLaw.objects.create(name="some area of law")
        self.assertEqual(str(aol), "some area of law")
        caol = CourtAreasOfLaw.objects.create(court=c, area_of_law=aol)
        self.assertEqual(str(caol), "Accrington Magistrates' Court deals with some area of law")
        country = Country.objects.get(name="England")
        self.assertEqual(str(country), "England")
        county = County.objects.create(name="some county", country=country)
        self.assertEqual(str(county), "some county")
        town = Town.objects.create(name="some town", county=county)
        self.assertEqual(str(town), "some town")
        address_type = AddressType.objects.create(name="some address type")
        self.assertEqual(str(address_type), "some address type")
        court_address = CourtAddress.objects.create(
            address_type=address_type,
            court=c,
            address="some address",
            postcode="some postcode",
            town=town
        )
        self.assertEqual(str(court_address), "some address type for Accrington Magistrates' Court is some address, some postcode, some town")
        contact_type = ContactType.objects.create(name="some contact type")
        self.assertEqual(str(contact_type), "some contact type")
        court_type = CourtType.objects.get(name="County Court")
        self.assertEqual(str(court_type), "County Court")
        court_contact = CourtContact.objects.create(contact_type=contact_type, court=c, value="some value")
        self.assertEqual(str(court_contact), "some contact type for Accrington Magistrates' Court is some value")
        court_court_type = CourtCourtTypes.objects.create(court=c, court_type=court_type)
        self.assertEqual(str(court_court_type), "Court type for Accrington Magistrates' Court is County Court")
        court_postcodes = CourtPostcodes.objects.create(court=c, postcode='SW11AA')
        self.assertEqual(str(court_postcodes), "Accrington Magistrates' Court covers SW11AA")
        la = LocalAuthority.objects.create(name="some local authority")
        self.assertEqual(str(la), "some local authority")
        claaol = CourtLocalAuthorityAreaOfLaw.objects.create(
            court=c, area_of_law=aol, local_authority=la
        )
        self.assertEqual(str(claaol), "Accrington Magistrates' Court covers some local authority for some area of law")
