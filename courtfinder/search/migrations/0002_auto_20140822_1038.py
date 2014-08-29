# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import abspath, basename, dirname, join, normpath
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, migrations


def enable_earthdistance(apps, schema_editor):
  schema_editor.execute('CREATE EXTENSION IF NOT EXISTS cube')
  schema_editor.execute('CREATE EXTENSION IF NOT EXISTS earthdistance')


def populate_database(apps, schema_editor):
  Court = apps.get_model('search', 'Court')
  AreaOfLaw = apps.get_model('search', 'AreaOfLaw')
  CourtAreasOfLaw = apps.get_model('search', 'CourtAreasOfLaw')
  CourtType = apps.get_model('search', 'CourtType')
  CourtCourtTypes = apps.get_model('search', 'CourtCourtTypes')
  AddressType = apps.get_model('search', 'AddressType')
  CourtAddress = apps.get_model('search', 'CourtAddress')
  Country = apps.get_model('search', 'Country')
  County = apps.get_model('search', 'County')
  Town = apps.get_model('search', 'Town')
  ContactType = apps.get_model('search', 'ContactType')
  CourtContact = apps.get_model('search', 'CourtContact')


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
      name=court_obj['name'],
      slug=court_obj['slug'],
      displayed=True,
      lat=court_obj['lat'],
      lon=court_obj['lon'],
      number=court_obj['court_number']
    )

    court.save()

    for aol_name in court_obj['areas_of_law']:
      try:
        aol = AreaOfLaw.objects.get(name=aol_name)
      except ObjectDoesNotExist:
        aol = AreaOfLaw.objects.create(name=aol_name)

      CourtAreasOfLaw.objects.create(court=court, area_of_law=aol)

    for court_type_name in court_obj['court_types']:
      try:
        ct = CourtType.objects.get(name=court_type_name)
      except ObjectDoesNotExist:
        ct = CourtType.objects.create(name=court_type_name)

      CourtCourtTypes.objects.create(court=court, court_type=ct)

    for address in court_obj['addresses']:
      try:
        address_type = AddressType.objects.get(name=address['type'])
      except ObjectDoesNotExist:
        address_type = AddressType.objects.create(name=address['type'])

      town = Town.objects.get(name=address['town'])

      CourtAddress.objects.create(
        court=court,
        address_type=address_type,
        address=address['address'],
        postcode=address['postcode'],
        town=town
      )

    for contact in court_obj['contacts']:
      try:
        contact_type = ContactType.objects.get(name=contact['type'])
      except ObjectDoesNotExist:
        contact_type = ContactType.objects.create(name=contact['type'])

        CourtContact.objects.create(
          court=court,
          contact_type=contact_type,
          value=contact['number']
        )


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
      migrations.RunPython(enable_earthdistance),
      migrations.RunPython(populate_database)
    ]
