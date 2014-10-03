from django.test import TestCase
from django.test import TestCase, Client

class SearchTestCase(TestCase):
    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/index.jinja')
        self.assertInHTML('<title>Find a court or tribunal - GOV.UK</title>', response.content, count=1)
