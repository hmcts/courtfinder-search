from django.core.management.base import BaseCommand
from django.conf import settings
from search.models import OpeningTime


class Command(BaseCommand):
    help = "Split opening data from description to type and hours on OpeningTime model"

    def handle(self, *args, **options):
        openings = OpeningTime.objects.all()
        for op in list(openings):
            description_split = op.description.split(':', 1)
            op.type = description_split[0]
            if op.description:
                if len(description_split) > 1:
                    type_hours = description_split[1]
                    type_hours = type_hours[1:]
                    op.hours = type_hours
            op.save()
