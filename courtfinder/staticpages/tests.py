from django.test import TestCase
from django.test import TestCase, Client
from django.conf import settings
from mock import Mock, patch

class SearchTestCase(TestCase):
    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/index.jinja')
        self.assertInHTML('<title>Find a court or tribunal - GOV.UK</title>', response.content, count=1)

    def test_feedback_page_returns_correct_content(self):
        c = Client()
        response = c.get('/feedback')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/feedback.jinja')
        self.assertInHTML('<title>Feedback for Court and Tribunal Finder</title>', response.content, count=1)

    def test_api_doc_returns_correct_content(self):
        c = Client()
        response = c.get('/api')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/api.jinja')
        self.assertInHTML('<title>Find a court or tribunal - API - GOV.UK</title>', response.content, count=1)
        response = c.get('/api.html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/api.jinja')
        self.assertInHTML('<title>Find a court or tribunal - API - GOV.UK</title>', response.content, count=1)

    def test_feedback_sent_page_returns_correct_content(self):
        with patch('django.core.mail.send_mail', Mock(return_value=2)):
            c = Client()
            settings.FEEDBACK_EMAIL_SENDER="sender@b.com"
            settings.FEEDBACK_EMAIL_RECEIVER="receiver@b.com"
            response = c.post('/feedback_submit',
                              {
                                  'feedback_text': 'I like it',
                                  'feedback_email': 'a@b.com',
                                  'feedback_referer': 'http://example.org',
                              },
                              follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'staticpages/feedback_sent.jinja')
            self.assertInHTML('<h1>Thank you for your feedback</h1>', response.content, count=1)
            response = c.post('/feedback_submit',
                              {
                                  'feedback_text': 'I like it',
                                  'feedback_referer': 'http://example.org',
                              },
                              follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'staticpages/feedback_sent.jinja')
            self.assertInHTML('<h1>Thank you for your feedback</h1>', response.content, count=1)

    def test_error_pages(self):
        c = Client()
        response = c.get('/403')
        self.assertEqual(response.status_code, 403)
        self.assertIn('Access denied', response.content)
        response = c.get('/404')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Page not found', response.content)
        response = c.get('/400')
        self.assertEqual(response.status_code, 400)
        self.assertIn('your browser sent a request that this server could not understand', response.content)
        response = c.get('/500')
        self.assertEqual(response.status_code, 500)
        self.assertIn('something went wrong', response.content)
