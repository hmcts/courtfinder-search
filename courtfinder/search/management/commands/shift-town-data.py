from django.core.management.base import BaseCommand
from django.conf import settings
from search.models import CourtAddress, Town


class Command(BaseCommand):
    help = "Move town data from separate table to fields on courtaddress"

    def handle(self, *args, **options):
        court_addresses = CourtAddress.objects.all().prefetch_related('town')
        for ca in list(court_addresses):
            if ca.town:
                town_obj = ca.town
                ca.town_name = town_obj.name
                ca.save()


