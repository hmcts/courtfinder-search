# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import abspath, basename, dirname, join, normpath
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, migrations

from search.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        data_dir = join(settings.PROJECT_ROOT, 'data')
        courts_data_path = join( data_dir, 'courts.json' )
        countries_data_path = join( data_dir, 'countries.json' )

        countries = []
        with open(countries_data_path, 'r') as countries_file:
            countries = json.load(countries_file)
            countries_file.close()

        for country in countries:
            c = Country(name=country['name'])
            c.save()

            for county in country['counties']:
                co = County(name=county['name'], country=c)
                co.save()

                for town in county['towns']:
                    if not Town.objects.filter(name=town).exists():
                        t = Town(name=town, county=co)
                        t.save()

        courts = []
        with open(courts_data_path, 'r') as courtsfile:
            courts = json.load(courtsfile)
            courtsfile.close()

        for court_obj in courts:
            court = Court(
                admin_id=court_obj['admin_id'],
                name=court_obj['name'],
                slug=court_obj['slug'],
                displayed=court_obj['display'],
                lat=court_obj['lat'],
                lon=court_obj['lon'],
                number=court_obj['court_number']
            )
            court.save()

            for aol_obj in court_obj['areas_of_law']:
                aol_name = aol_obj['name']
                aol_councils = aol_obj['councils']

                aol, created = AreaOfLaw.objects.get_or_create(name=aol_name)

                CourtAreasOfLaw.objects.create(court=court, area_of_law=aol)

                for council_name in aol_councils:
                    council, created = LocalAuthority.objects.get_or_create(name=council_name)

                    CourtLocalAuthorityAreaOfLaw.objects.create(
                        court=court,
                        area_of_law=aol,
                        local_authority=council
                    )

            for court_type_name in court_obj['court_types']:
                ct, created = CourtType.objects.get_or_create(name=court_type_name)

                CourtCourtTypes.objects.create(court=court, court_type=ct)


            for address in court_obj['addresses']:
                address_type, created = AddressType.objects.get_or_create(name=address['type'])
                town = Town.objects.get(name=address['town'])

                CourtAddress.objects.create(
                    court=court,
                    address_type=address_type,
                    address=address['address'],
                    postcode=address['postcode'],
                    town=town
                )

            for contact in court_obj['contacts']:
                contact_type, created = ContactType.objects.get_or_create(name=contact['type'])

                CourtContact.objects.create(
                    court=court,
                    contact_type=contact_type,
                    value=contact['number']
                )

            for postcode in court_obj['postcodes']:
                CourtPostcodes.objects.create(
                    court=court,
                    postcode=postcode
                )
