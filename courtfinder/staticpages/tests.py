import json
from mock import Mock, patch

from django.test import TestCase, Client
from django.conf import settings

from search.ingest import Ingest
from .forms import FeedbackForm


class SearchTestCase(TestCase):

    def setUp(self):
        test_data_dir = settings.PROJECT_ROOT +  '/data/test_data/'
        courts_json_1 = open(test_data_dir + 'courts.json').read()
        imports = json.loads(courts_json_1)
        Ingest.courts(imports['courts'])
        Ingest.emergency_message(imports['emergency_message'])

    def test_top_page_returns_correct_content(self):
        c = Client()
        response = c.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.jinja')
        self.assertInHTML('<title>Find the right court or tribunal</title>', response.content, count=1)

    def test_feedback_page_returns_correct_content(self):
        c = Client()
        response = c.get('/feedback')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/feedback.jinja')
        self.assertInHTML('<title>Court and Tribunal Finder - Feedback</title>', response.content, count=1)

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

    def test_court_id_redirect(self):
        c = Client()
        r = c.get('/courts/accrington-magistrates-court')
        r = c.get('/?court_id=7')
        self.assertRedirects(r, '/courts/accrington-magistrates-court', 302)
        r = c.get('/?court_id=2038')
        self.assertEqual(r.status_code, 404)

class FeedbackFormTestCase(TestCase):

    def setUp(self):
        self.post_data = {
            "feedback_text": "ra ra ra",
            "feedback_referer": "www.a.url.com",
            "feedback_email": "",
            "feedback_name": ""
        }

    def test_form_honeypot_field_invalid_if_not_empty(self):

        self.post_data["feedback_name"] = "should be empty"

        form = FeedbackForm(self.post_data)

        self.assertFalse(form.is_valid())

    def test_form_honeypot_field_valid_if_empty(self):

        form = FeedbackForm(self.post_data)

        self.assertTrue(form.is_valid())


