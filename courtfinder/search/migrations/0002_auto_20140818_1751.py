# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def initialise_countries(apps, schema_editor):
    countries = ['England', 'Northern Ireland', 'Scotland', 'Wales']
    Country = apps.get_model('search', 'Country')

    for country in countries:
        c = Country(name=country)
        c.save()


def initialise_areas_of_law(apps, schema_editor):
    areas_of_law = [
        'Adoption', 'Bankruptcy', 'Children', 'Civil partnership', 'Crime', 
        'Divorce', 'Domestic violence', 'Employment', 'Forced marriage', 
        'High court', 'Housing possession', 'Immigration', 'Money claims', 
        'Probate', 'Social security'
    ]
    AreaOfLaw = apps.get_model('search', 'AreaOfLaw')

    for aol in areas_of_law:
        a = AreaOfLaw(name=aol)
        a.save()


def initialise_court_types(apps, schema_editor):
    court_types = ["County Court", "Magistrates Court", "Crown Court", "Tribunal", "Family court"]

    CourtType = apps.get_model('search', 'CourtType')

    for ct in court_types:
        c = CourtType(name=ct)
        c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
      migrations.RunPython(initialise_countries),
      migrations.RunPython(initialise_areas_of_law),
      migrations.RunPython(initialise_court_types),
    ]
