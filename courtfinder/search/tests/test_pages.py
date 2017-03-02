import json
from django.test import TestCase, Client
from search.models import *
from django.conf import settings
from search.ingest import Ingest

class SearchPageTestCase(TestCase):

    def setUp(self):
        test_data_dir = settings.PROJECT_ROOT +  '/data/test_data/'
        courts_json_1 = open(test_data_dir + 'courts.json').read()
        imports = json.loads(courts_json_1)
        Ingest.courts(imports['courts'])
        Ingest.emergency_message(imports['emergency_message'])
        DataStatus.objects.create(data_hash='415d49233b8592cf5195b33f0eddbdc86cebc72f2d575d392e941a53c085281a')

    def tearDown(self):
        pass

    def test_top_page_sans_slash_redirects_to_slash(self):
        c = Client()
        response = c.get('/search')
        self.assertRedirects(response, '/search/', 301)


    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.jinja')
        self.assertIn('Find the right court or tribunal', response.content)


    def test_postcode_page(self):
        c = Client()
        response = c.get('/search/postcode?aol=Divorce&spoe=start')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/postcode.jinja')
        self.assertIn('Enter postcode', response.content)
