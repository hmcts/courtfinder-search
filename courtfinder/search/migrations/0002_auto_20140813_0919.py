# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def initialise_countries(apps, schema_editor):
  countries = ['England', 'Northern Ireland', 'Scotland', 'Wales']
  Country = apps.get_model('search', 'Country')

  for country in countries:
    c = Country(name=country)
    c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
      migrations.RunPython(initialise_countries)
    ]
