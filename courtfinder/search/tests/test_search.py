import requests
import json
import re
from django.test import TestCase, Client
from mock import Mock, patch
from search.court_search import CourtSearch, CourtSearchError, CourtSearchClientError, CourtSearchInvalidPostcode
from search.models import *
from django.conf import settings
from search.ingest import Ingest


class SearchTestCase(TestCase):

    def setUp(self):
        test_data_dir = settings.PROJECT_ROOT +  '/data/test_data/'
        courts_json_1 = open(test_data_dir + 'courts.json').read()
        Ingest.courts(json.loads(courts_json_1))
        DataStatus.objects.create(data_hash='415d49233b8592cf5195b33f0eddbdc86cebc72f2d575d392e941a53c085281a')

    def tearDown(self):
        pass

    def test_format_results_with_postal_address(self):
        c = Client()
        response = c.get('/search/results?q=Accrington')
        self.assertIn("Blackburn", response.content)

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
        self.assertIn('<h1>Children</h1>', response.content)

    def test_spoe_page_with_children_start_proceedings(self):
        c = Client()
        response = c.get('/search/spoe?aol=Children')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/spoe.jinja')
        self.assertIn('I want to start new proceedings', response.content)

    def test_spoe_page_with_children_in_contact(self):
        c = Client()
        response = c.get('/search/spoe?aol=Children')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/spoe.jinja')
        self.assertIn('I am already in contact', response.content)

    def test_spoe_page_with_children_in_contact_search_courts(self):
        c = Client()
        response = c.get('/search/searchbyPostcodeOrCourtList?aol=Children&spoe=continue', follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(status_code, 302)
        self.assertTemplateUsed(response, 'courts/list.jinja')

    def test_spoe_page_with_children_start_search_postcode(self):
        c = Client()
        response = c.get('/search/searchbyPostcodeOrCourtList?aol=Children&spoe=start', follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(status_code, 302)
        self.assertTemplateUsed(response, 'search/postcode.jinja')

    def test_spoe_page_with_has_spoe_Divorce(self):
        c = Client()
        response = c.get('/search/spoe?aol=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/spoe.jinja')
        self.assertIn('<h1>About your Divorce</h1>', response.content)

    def test_spoe_page_with_divorce_proceedings(self):
        c = Client()
        response = c.get('/search/spoe?aol=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/spoe.jinja')
        self.assertIn('I want to start proceedings', response.content)

    def test_spoe_page_with_divorce_in_contact(self):
        c = Client()
        response = c.get('/search/spoe?aol=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/spoe.jinja')
        self.assertIn('I am already in contact with a court', response.content)

    def test_spoe_page_with_divorce_postcode_start(self):
        c = Client()
        response = c.get('/search/postcode?aol=Divorce&spoe=start')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/postcode.jinja')
        self.assertIn('You will be directed to your Regional Divorce Centre.', response.content)

    def test_spoe_page_with_divorce_postcode_continue(self):
        c = Client()
        response = c.get('/search/postcode?aol=Divorce&spoe=continue')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/postcode.jinja')
        self.assertIn('You will be directed to your Regional Divorce Centre.', response.content)

    def test_spoe_page_with_divorce_in_contact_search_courts(self):
        c = Client()
        response = c.get('/search/searchbyPostcodeOrCourtList?aol=Divorce&spoe=continue', follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(status_code, 302)
        self.assertTemplateUsed(response, 'courts/list.jinja')

    def test_spoe_page_with_divorce_start_search_postcode(self):
        c = Client()
        response = c.get('/search/searchbyPostcodeOrCourtList?aol=Divorce&spoe=start', follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(status_code, 302)
        self.assertTemplateUsed(response, 'search/postcode.jinja')


    def test_spoe_page_without_spoe(self):
        c = Client()
        response = c.get('/search/spoe?aol=Crime', follow=True)
        self.assertIn('<h1>Enter postcode</h1>', response.content)

    def test_distance_search(self):
        c = Client()
        response = c.get('/search/results?postcode=SE154UH&aol=Crime')
        self.assertEqual(response.status_code, 200)

    def test_local_authority_search(self):
        c = Client()
        response = c.get('/search/results?postcode=SE154UH&aol=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Accrington',response.content)

    def test_results_no_query(self):
        c = Client()
        response = c.get('/search/results?q=')
        self.assertRedirects(response, '/search/address?error=noquery', 302)

    def test_results_no_postcode(self):
        c = Client()
        response = c.get('/search/results?aol=Crime&postcode=')
        self.assertRedirects(response, '/search/postcode?error=nopostcode&aol=Crime', 302)

    def test_results_cases_heard(self):
        c = Client()
        response = c.get('/search/results?q=Accrington')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cases heard at this venue', response.content)

    def test_sample_postcode_all_aols(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&aol=All')
        self.assertEqual(response.status_code, 200)

    def test_postcode_aol_Housing(self):
        c = Client()
        response = c.get('/search/postcode?aol=Housing possession')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/postcode.jinja')
        self.assertIn('<h1>Housing Possession</h1>', response.content)

    def test_sample_postcode_specific_aol(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&aol=Divorce')
        self.assertEqual(response.status_code, 200)

    def test_bad_aol(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15+4UH&aol=doesntexist', follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn('your browser sent a request',response.content)

    def test_inactive_court_is_not_displaying_in_address_search_results(self):
        c = Client()
        response = c.get('/search/results?q=Some+old', follow=True)
        self.assertIn('<span id="number-of-results">1</span>', response.content)

    def test_address_search_single_inactive_court_result_redirects_to_closed_court(self):
        c = Client()
        response = c.get('/search/results?q=Some+old+closed+court', follow=True)
        self.assertIn('alert', response.content)

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

    def test_redirect_directive_action(self):
        with patch('search.rules.Rules.for_view', Mock(return_value={'action':'redirect', 'target':'search:postcode'})):
            c = Client()
            response = c.get('/search/results?postcode=BLARGH')
            self.assertRedirects(response, '/search/postcode?postcode=BLARGH&error=badpostcode', 302)

    def test_internal_error(self):
        c = Client()
        with patch('search.court_search.CourtSearch.get_courts', Mock(side_effect=CourtSearchError('something went wrong'))):
            response = c.get('/search/results.json?q=Accrington')
            self.assertEquals(500, response.status_code)
            self.assertIn("something went wrong", response.content)

    def test_search_no_postcode_nor_q(self):
        c = Client()
        response = c.get('/search/results')
        self.assertRedirects(response, '/search/', 302)

    def test_postcode_to_local_authority_short_postcode(self):
        self.assertEqual(len(CourtSearch(postcode='SE15', area_of_law='Divorce')
                             .get_courts()), 1)

    def test_local_authority_search_ordered(self):
        self.assertEqual(CourtSearch(postcode='SE154UH', area_of_law='Divorce')
                         .get_courts()[0].name, "Accrington Magistrates' Court")

    def test_proximity_search(self):
        self.assertNotEqual(CourtSearch(postcode='SE154UH',
                                        area_of_law='Divorce').get_courts(), [])

    def test_court_address_search_error(self):
        with patch('search.court_search.CourtSearch.get_courts',
                   Mock(side_effect=CourtSearchError('something went wrong'))):
            c = Client()
            with self.assertRaises(CourtSearchError):
                response = c.get('/search/results?q=Accrington')

    def test_court_postcode_search_error(self):
        with patch('search.court_search.CourtSearch.get_courts',
                   Mock(side_effect=CourtSearchError('something went wrong'))):
            c = Client()
            with self.assertRaises(CourtSearchError):
                response = c.get('/search/results?postcode=SE15+4PE')

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

    def test_empty_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=')
        self.assertEqual(response.status_code, 302)

    def test_broken_postcode(self):
        c = Client()
        response = c.get('/search/results?aol=Divorce&spoe=continue&postcode=NW3+%25+au', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('NW3  au', response.content)

    def test_ni(self):
        c = Client()
        response = c.get('/search/results?postcode=bt2&aol=Divorce', follow=True)
        self.assertIn("this tool does not return results for Northern Ireland", response.content)

    def test_money_claims(self):
        c = Client()
        response = c.get('/search/results?postcode=sw1h9aj&spoe=start&aol=Money+claims')
        self.assertIn("CCMCC", response.content)

    def test_money_claims_heading(self):
        c = Client()
        response = c.get('/search/spoe?aol=Money claims')
        self.assertIn('<h1>About your money claim</h1>', response.content)

    def test_money_claims_landing_page_option2(self):
        c = Client()
        response = c.get('/search/spoe?aol=Money claims')
        self.assertIn('already have a claim', response.content)

    def test_money_claims_new_claim(self):
        c = Client()
        response = c.get('/search/postcode?aol=Money claims&spoe=start')
        self.assertIn('<h1>For a new claim :-</h1>', response.content)

    def test_money_claims_new_claim_ccmcc(self):
        c = Client()
        response = c.get('/search/postcode?aol=Money claims&spoe=start')
        self.assertIn('courts/county-court-money-claims-centre-ccmcc', response.content)

    def test_money_claims_existing(self):
        c = Client()
        response = c.get('/search/postcode?aol=Money claims&spoe=continue')
        self.assertIn('<h1>For an existing claim :-</h1>', response.content)

    def test_money_claims_existing_online(self):
        c = Client()
        response = c.get('/search/postcode?aol=Money claims&spoe=continue')
        self.assertIn('That was previously entered online', response.content)
        self.assertIn('https://www.gov.uk/make-money-claim-online', response.content)

    def test_money_claims_existing_paper(self):
        c = Client()
        response = c.get('/search/postcode?aol=Money claims&spoe=continue')
        self.assertIn('That was previously completed on paper', response.content)
        self.assertIn('/courts/county-court-money-claims-centre-ccmcc', response.content)

    def test_money_claims_existing_court_known(self):
        c = Client()
        response = c.get('/search/postcode?aol=Money claims&spoe=continue')
        self.assertIn('If you know a local court is dealing with your claim', response.content)
        self.assertIn('/courts/', response.content)

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
        aol = AreaOfLaw.objects.create(name="Divorce",
                                        external_link="http://www.gov.uk/child-adoption",
                                        external_link_desc="More information on adoption.")
        self.assertEqual(str(aol), "Divorce")
        self.assertEqual(str(aol.external_link), "http://www.gov.uk/child-adoption")
        self.assertEqual(str(aol.external_link_desc), "More information on adoption.")
        aols = CourtAreaOfLaw.objects.create(court=court, area_of_law=aol)
        self.assertEqual(str(aols), "Accrington Magistrates' Court deals with Divorce (spoe: False)")
        town = Town.objects.create(name="Hobbittown", county="Shire")
        self.assertEqual(str(town), "Hobbittown (Shire)")
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

    def test_data_status(self):
        c = Client()
        response = c.get('/search/datastatus')
        self.assertEqual(200, response.status_code)
        self.assertIn('415d49233b8592cf5195b33f0eddbdc86cebc72f2d575d392e941a53c085281a', response.content)

    def test_employment_venues_link_in_search_results(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15&aol=Employment')
        self.assertEqual(200, response.status_code)
        self.assertIn('https://www.gov.uk/guidance/employment-tribunal-offices-and-venues', response.content)

    def test_child_support_venues_link_in_search_results(self):
        c = Client()
        response = c.get('/search/results?aol=Children&spoe=continue&postcode=SE15')
        self.assertEqual(200, response.status_code)
        self.assertIn('http://sscs.venues.tribunals.gov.uk/venues/venues.htm', response.content)

    def test_social_security_venues_link_in_search_results(self):
        c = Client()
        response = c.get('/search/results?aol=Social+security&postcode=SE15')
        self.assertEqual(200, response.status_code)
        self.assertIn('http://sscs.venues.tribunals.gov.uk/venues/venues.htm', response.content)

    def test_for_no_venue_links(self):
        c = Client()
        response = c.get('/search/results?aol=Bankruptcy&postcode=SE15')
        self.assertEqual(200, response.status_code)
        self.assertNotIn('https://www.gov.uk/guidance/employment-tribunal-offices-and-venues', response.content)
        self.assertNotIn('http://sscs.venues.tribunals.gov.uk/venues/venues.htm', response.content)
        
    def test_gov_uk_links_exist(self):
        
        aol = AreaOfLaw.objects.get(name="Bankruptcy")
        c = Client()
        response = c.get('/search/results?aol=Bankruptcy&postcode=SW1H9AJ')
        self.assertEqual(200, response.status_code)
        self.assertIn('https://www.gov.uk/bankruptcy', response.content)
        self.assertIn('More information on bankruptcy.', response.content)