from django.test import TestCase, Client
from django.conf import settings
from django.core import management
from django.core.management.commands import loaddata
from search.models import DataStatus

class CourtCodeTestCase(TestCase):

    def setUp(self):
        test_data_dir = settings.PROJECT_ROOT + '/data/test_data/'
        management.call_command('loaddata', test_data_dir + 'test_data.yaml', verbosity=0)
        DataStatus.objects.create(data_hash='415d49233b8592cf5195b33f0eddbdc86cebc72f2d575d392e941a53c085281a')

    def test_non_existing(self):
        c = Client()

        response = c.get('/search/results?courtcode=123', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('validation-error', response.content)

    def test_exists(self):
        c = Client()

        response = c.get('/search/results?courtcode=1725', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Accrington", response.content)
        self.assertNotIn('validation-error', response.content)
