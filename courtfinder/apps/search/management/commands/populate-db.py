# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from os.path import join
import json
import hashlib

from django.core.management.base import BaseCommand
from django.conf import settings

from search.models import DataStatus
from search.ingest import Ingest


class Command(BaseCommand):

    def import_files(self, data_dir):
        courts_data_path = join(data_dir, 'courts.json')
        courts = []
        with open(courts_data_path, 'r') as courtsfile:
            print "courts file found"
            courts = json.load(courtsfile)
            courtsfile.close()
        print "Starting data import"
        Ingest.courts(courts)
        print "OK"

    def hashes(self, dir, filenames):
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        hashes = []
        for filename in filenames:
            try:
                with open(dir+'/'+filename, 'rb') as afile:
                    buf = afile.read(BLOCKSIZE)
                    while len(buf) > 0:
                        hasher.update(buf)
                        buf = afile.read(BLOCKSIZE)
                hashes.append(hasher.hexdigest())
            except:
                hashes.append(None)
        return hashes

    def handle(self, *args, **options):

        print "Computing hashes of existing files"
        # determine where the json files are
        try:
            S3_KEY = os.environ['S3_KEY']
            S3_SECRET = os.environ['S3_SECRET']
            S3_BUCKET = os.environ['S3_BUCKET']
            data_dir = '/tmp'
            environment = 'S3'
            old_hashes = self.hashes(data_dir, ['courts.json'])
        except:
            print (
                "I didn't find the environment variables: S3_KEY, "
                "S3_SECRET, S3_BUCKET.")
            print "Trying to find files locally instead"
            if len(args) == 1:
                data_dir = join(settings.PROJECT_ROOT, args[0])
            else:
                data_dir = join(settings.PROJECT_ROOT, 'data')
            print "looking for json data in "+data_dir
            environment = 'local'

        if environment == 'S3':
            print "Importing from S3...",

            import boto

            # connect to the bucket
            conn = boto.connect_s3(S3_KEY, S3_SECRET)
            bucket = conn.get_bucket(S3_BUCKET)

            # go through the list of files
            bucket_list = bucket.list()
            for l in bucket_list:
                keyString = str(l.key)
                l.get_contents_to_filename(join(data_dir, keyString))
            print "done"

            print "Computing hashes of new files"
            new_hashes = self.hashes(data_dir, ['courts.json'])
            if new_hashes != old_hashes:
                print "hashes differ. Importing the new files"
                self.import_files(data_dir)
            else:
                print "same hashes. Not importing."
        else:
            print "Importing from local files..."
            self.import_files(data_dir)
            new_hashes = self.hashes(data_dir, ['courts.json'])

        print "Success"
        print "Storing data state...",
        DataStatus.objects.create(data_hash=''.join(new_hashes))
        print "OK"
        print "All done"
