# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import abspath, basename, dirname, join, normpath
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, migrations

from search.ingest import Ingest

class Command(BaseCommand):


    def handle(self, *args, **options):
        data_dir = join(settings.PROJECT_ROOT, 'data')
        courts_data_path = join( data_dir, 'courts.json' )
        countries_data_path = join( data_dir, 'countries.json' )

        countries = []
        with open(countries_data_path, 'r') as countries_file:
            countries = json.load(countries_file)
            countries_file.close()
        Ingest.countries(countries)

        courts = []
        with open(courts_data_path, 'r') as courtsfile:
            courts = json.load(courtsfile)
            courtsfile.close()
        Ingest.courts(courts)
