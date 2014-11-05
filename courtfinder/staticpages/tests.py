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
            response = c.post('/feedback-sent', { 'feedback_text': 'I like it',
                                                  'feedback_email': 'a@b.com' })
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'staticpages/feedback_sent.jinja')
            self.assertInHTML('<h1>Thank you for your feedback</h1>', response.content, count=1)
