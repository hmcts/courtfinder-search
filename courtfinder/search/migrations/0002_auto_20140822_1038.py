# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import abspath, basename, dirname, join, normpath
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, migrations


def enable_earthdistance(apps, schema_editor):
  schema_editor.execute('CREATE EXTENSION cube')
  schema_editor.execute('CREATE EXTENSION earthdistance')


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
      lon=court_obj['lon']
    )
    
    court.save()

    for aol_name in court_obj['areas_of_law']:
      try:
        aol = AreaOfLaw.objects.get(name=aol_name)
      except ObjectDoesNotExist:
        aol = AreaOfLaw(name=aol_name)
        aol.save()

      caol = CourtAreasOfLaw(court=court, area_of_law=aol)
      caol.save()

    for court_type_name in court_obj['court_types']:
      try:
        ct = CourtType.objects.get(name=court_type_name)
      except ObjectDoesNotExist:
        ct = CourtType(name=court_type_name)
        ct.save()

      cct = CourtCourtTypes(court=court, court_type=ct)
      cct.save()

    for address in court_obj['addresses']:
      try:
        address_type = AddressType.objects.get(name=address['type'])
      except ObjectDoesNotExist:
        address_type = AddressType(name=address['type'])
        address_type.save()

      town = Town.objects.get(name=address['town'])

      ca = CourtAddress(
        court=court,
        address_type=address_type,
        address=address['address'],
        postcode=address['postcode'],
        town=town
      )

      ca.save()


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
      migrations.RunPython(enable_earthdistance),
      migrations.RunPython(populate_database)
    ]
