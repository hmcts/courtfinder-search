from django.test import TestCase, Client

class SearchTestCase(TestCase):

    def test_top_page_sans_slash_redirects_to_slash(self):
        c = Client()
        response = c.get('/search')
        print response
        self.assertRedirects(response, '/search/', 301)

    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.jinja')
        self.assertInHTML('<title>Find a court or tribunal</title>', response.content, count=1)
