from django.test import TestCase, Client

class SearchPageTestCase(TestCase):


    def test_top_page_sans_slash_redirects_to_slash(self):
        c = Client()
        response = c.get('/search')
        self.assertRedirects(response, '/search/', 301)


    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.jinja')
        self.assertIn('Find the right court of tribunal', response.content)

    def test_aol_page(self):
        c = Client()
        response = c.get('/search/aol')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/aol.jinja')
        self.assertIn('About your issue', response.content)

    def test_spoe_page(self):
        c = Client()
        response = c.get('/search/spoe?aol=Divorce')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/spoe.jinja')
        self.assertIn('About your issue', response.content)

    def test_postcode_page(self):
        c = Client()
        response = c.get('/search/postcode?aol=Divorce&spoe=start')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/postcode.jinja')
        self.assertIn('Enter postcode', response.content)
