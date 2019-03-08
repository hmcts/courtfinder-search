from django.core.management.base import BaseCommand
from search.models import Email, OpeningTime, Facility
import csv


class Command(BaseCommand):
    help = "Ensure that emails, opening time and facility objects are not shared between courts"

    def handle(self, *args, **options):
        ecount = 0
        fcount = 0
        otcount = 0
        all_courts_affected = set()
        for email in Email.objects.all():
            ce_set = email.courtemail_set.all()
            if ce_set.count() > 1:
                all_courts_affected.add(ce_set.first().court.name)
                ecount += 1
                for ce in ce_set[1::]:
                    all_courts_affected.add(ce.court.name)
                    new_obj = email
                    new_obj.pk = None
                    new_obj.save()
                    ce.email = new_obj
                    ce.save()
        print("number of shared emails: " + str(ecount))
        for facility in Facility.objects.all():
            cf_set = facility.courtfacility_set.all()
            if cf_set.count() > 1:
                all_courts_affected.add(cf_set.first().court.name)
                fcount += 1
                for cf in cf_set[1::]:
                    all_courts_affected.add(cf.court.name)
                    new_obj = facility
                    new_obj.pk = None
                    new_obj.save()
                    cf.facility = new_obj
                    cf.save()
        print("number of shared facilities: " + str(fcount))
        for ot in OpeningTime.objects.all():
            cot_set = ot.courtopeningtime_set.all()
            if cot_set.count() > 1:
                all_courts_affected.add(cot_set.first().court.name)
                otcount += 1
                for cot in cot_set[1::]:
                    all_courts_affected.add(cot.court.name)
                    new_obj = ot
                    new_obj.pk = None
                    new_obj.save()
                    cot.opening_time = new_obj
                    cot.save()
        print("number of shared opening times" + str(otcount))
        with open("courts affected.csv", "w") as cw:
            writer = csv.writer(cw, lineterminator='\n')
            for c in list(all_courts_affected):
                writer.writerow([str(c)])