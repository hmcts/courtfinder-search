from django.test import TestCase
from search.models import Court

class CourtCodeTestCase(TestCase):

    def test_slug_updates_with_name(self):
        court = Court()
        court.name = 'old name'
        court.slug = 'old-slug'

        court.update_name_slug('testing new slug')

        self.assertEqual('testing new slug', court.name)
        self.assertEqual('testing-new-slug', court.slug)