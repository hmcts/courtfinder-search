from django.test import TestCase, Client

class SearchPageTestCase(TestCase):
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
        ])

    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.jinja')
        self.assertInHTML('<title>Find a court or tribunal</title>', response.content, count=1)

    def test_list_page_returns_correct_content(self):
        c = Client()
        response = c.get('/search/list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/list.jinja')
        self.assertInHTML('<title>Courts and Tribunals</title>', response.content, count=1)
        self.assertInHTML('<h2 class="clear letterheader">A</h2>', response.content, count=1)

    def test_list_page_letter_returns_correct_content(self):
        c = Client()
        response = c.get('/search/list/C')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/list.jinja')
        self.assertInHTML('<title>Courts and Tribunals</title>', response.content, count=1)
        self.assertInHTML('<h2 class="clear letterheader">C</h2>', response.content, count=1)
