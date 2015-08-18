from django.core.urlresolvers import reverse
from django.test import Client
from django.utils.timezone import now

from courtfinder.test_utils import TestCaseWithData
from search.models import SearchStatistic
from search.tests.test_search import valid_response


class SearchStatisticsTestCase(TestCaseWithData):

    def test_latest_search(self):
        client = Client()
        with valid_response('lookup_postcode'):
            self.assertIsNone(SearchStatistic.get_latest_search())
            response = client.get(reverse('search:results'), data={
                'aol': 'crime',
                'postcode': 'SW1A 1AA',
            })
            self.assertEqual(response.status_code, 200)
            latest_search = SearchStatistic.get_latest_search()
            self.assertIsNotNone(latest_search)
            self.assertLess(latest_search, now())

    def test_pingdom_doesnt_count(self):
        client = Client(
            HTTP_USER_AGENT='Pingdom.com_bot_version_1.4_(http://www.pingdom.com/)')
        with valid_response('lookup_postcode'):
            self.assertIsNone(SearchStatistic.get_latest_search())
            response = client.get(reverse('search:results'), data={
                'aol': 'crime',
                'postcode': 'SW1A 1AA',
            })
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(SearchStatistic.get_latest_search())
