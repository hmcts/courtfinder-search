from django.test import Client
from django.conf import settings
from mock import Mock, patch
from courtfinder.test_utils import TestCaseWithData


class SearchTestCase(TestCaseWithData):
    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.jinja')
        self.assertInHTML(
            '<title>Find the right court or tribunal</title>', response.content, count=1)

    def test_feedback_page_returns_correct_content(self):
        c = Client()
        response = c.get('/feedback')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/feedback.jinja')
        self.assertInHTML(
            '<title>Feedback for Court and Tribunal Finder</title>', response.content, count=1)

    def test_api_doc_returns_correct_content(self):
        c = Client()
        response = c.get('/api')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/api.jinja')
        self.assertInHTML(
            '<title>Find a court or tribunal - API - GOV.UK</title>', response.content, count=1)
        response = c.get('/api.html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/api.jinja')
        self.assertInHTML(
            '<title>Find a court or tribunal - API - GOV.UK</title>', response.content, count=1)

    def test_feedback_sent_page_returns_correct_content(self):
        with patch('django.core.mail.send_mail', Mock(return_value=2)):
            c = Client()
            settings.FEEDBACK_EMAIL_SENDER = "sender@b.com"
            settings.FEEDBACK_EMAIL_RECEIVER = "receiver@b.com"
            response = c.post('/feedback_submit',
                              {
                                  'feedback_text': 'I like it',
                                  'feedback_email': 'a@b.com',
                                  'feedback_referer': 'http://example.org',
                              },
                              follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(
                response, 'staticpages/feedback_sent.jinja')
            self.assertInHTML(
                '<h1>Thank you for your feedback</h1>', response.content, count=1)
            response = c.post('/feedback_submit',
                              {
                                  'feedback_text': 'I like it',
                                  'feedback_referer': 'http://example.org',
                              },
                              follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(
                response, 'staticpages/feedback_sent.jinja')
            self.assertInHTML(
                '<h1>Thank you for your feedback</h1>', response.content, count=1)

    def test_court_id_redirect(self):
        c = Client()
        r = c.get('/courts/accrington-magistrates-court')
        r = c.get('/?court_id=7')
        self.assertRedirects(r, '/courts/accrington-magistrates-court', 302)
        r = c.get('/?court_id=2038')
        self.assertEqual(r.status_code, 404)
