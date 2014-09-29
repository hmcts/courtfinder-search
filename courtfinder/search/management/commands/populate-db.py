# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from os.path import abspath, basename, dirname, join, normpath
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, migrations

from search.ingest import Ingest

class Command(BaseCommand):

    def import_files(self, data_dir):
        courts_data_path = join( data_dir, 'courts.json' )
        countries_data_path = join( data_dir, 'countries.json' )
        countries = []
        with open(countries_data_path, 'r') as countries_file:
            print "countries file found"
            countries = json.load(countries_file)
            countries_file.close()
        Ingest.countries(countries)
        courts = []
        with open(courts_data_path, 'r') as courtsfile:
            print "courts file found"
            courts = json.load(courtsfile)
            courtsfile.close()
        print "Starting data import"
        Ingest.courts(courts)
        print "OK"

    def handle(self, *args, **options):
        try:
            print "Trying to import from S3"
            S3_KEY=os.environ['S3_KEY']
            S3_SECRET=os.environ['S3_SECRET']
            S3_BUCKET=os.environ['S3_BUCKET']

            # all the environment variables are here, let's get the files from s3
            import boto
            from boto.s3.key import Key

            # connect to the bucket
            conn = boto.connect_s3(S3_KEY, S3_SECRET)
            bucket = conn.get_bucket(S3_BUCKET)

            # go through the list of files
            bucket_list = bucket.list()
            data_dir = '/tmp'
            for l in bucket_list:
                keyString = str(l.key)
                l.get_contents_to_filename(join(data_dir,keyString))
            print "done"

        except KeyError:
            print "I didn't find the environment variables: S3_KEY, S3_SECRET, S3_BUCKET."
            print "Trying to find files locally instead"
            data_dir = join(settings.PROJECT_ROOT, 'data')

        self.import_files(data_dir)
        print "all done"
