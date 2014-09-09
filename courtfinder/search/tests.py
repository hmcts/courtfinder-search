from django.test import TestCase, Client

class SearchTestCase(TestCase):

    def test_top_page_sans_slash_redirects_to_slash(self):
        c = Client()
        response = c.get('/search')
        self.assertRedirects(response, '/search/', 301)

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

    def test_partial_postcode(self):
        c = Client()
        response = c.get('/search/results?postcode=SE15&area_of_law=All')
        self.assertEqual(response.status_code, 200)

    def test_address_search(self):
        c = Client()
        response = c.get('/search/results?q=Leeds')
        self.assertEqual(response.status_code, 200)
