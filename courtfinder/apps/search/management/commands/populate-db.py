# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import hashlib

from django.core.management.base import BaseCommand
from django.conf import settings

from search.models import DataStatus
from search.ingest import Ingest


class Command(BaseCommand):
    verbosity = 1

    def print_info(self, msg, ending=None):
        if self.verbosity:
            self.stdout.write(msg, ending=ending)

    def import_files(self, data_dir):
        courts_data_path = os.path.join(data_dir, 'courts.json')
        with open(courts_data_path, 'r') as courtsfile:
            self.print_info('Courts file found')
            courts = json.load(courtsfile)
            courtsfile.close()
        self.print_info('Starting data import')
        Ingest.courts(courts)
        self.print_info('OK')

    @classmethod
    def hashes(cls, dir_path, filenames):
        block_size = 65536
        hasher = hashlib.md5()
        hashes = []
        for filename in filenames:
            try:
                with open(dir_path + '/' + filename, 'rb') as afile:
                    buf = afile.read(block_size)
                    while len(buf) > 0:
                        hasher.update(buf)
                        buf = afile.read(block_size)
                hashes.append(hasher.hexdigest())
            except (IOError, Exception):
                hashes.append(None)
        return hashes

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])
        self.print_info('Computing hashes of existing files')
        # determine where the json files are
        try:
            s3_key = os.environ['S3_KEY']
            s3_secret = os.environ['S3_SECRET']
            s3_bucket = os.environ['S3_BUCKET']
            data_dir = '/tmp'
            environment = 'S3'
        except KeyError:
            s3_key, s3_secret, s3_bucket = None, None, None
            self.print_info("I didn't find the environment variables: S3_KEY, S3_SECRET, S3_BUCKET.")
            self.print_info('Trying to find files locally instead')
            if len(args) == 1:
                data_dir = os.path.join(settings.PROJECT_ROOT, args[0])
            else:
                data_dir = os.path.join(settings.PROJECT_ROOT, 'data')
            self.print_info('Looking for json data in ' + data_dir)
            environment = 'local'

        if environment == 'S3':
            new_hashes = self.handle_s3(s3_bucket, s3_key, s3_secret, data_dir)
        else:
            new_hashes = self.handle_local(data_dir)

        self.print_info('Success')
        self.print_info('Storing data state...', ending=' ')
        DataStatus.objects.create(data_hash=''.join(new_hashes))
        self.print_info('OK')
        self.print_info('All done')

    def handle_local(self, data_dir):
        self.print_info('Importing from local files...')
        self.import_files(data_dir)
        new_hashes = self.hashes(data_dir, ['courts.json'])
        return new_hashes

    def handle_s3(self, s3_bucket, s3_key, s3_secret, data_dir):
        old_hashes = self.hashes(data_dir, ['courts.json'])

        self.print_info('Importing from S3...', ending=' ')

        import boto

        # connect to the bucket
        conn = boto.connect_s3(s3_key, s3_secret)
        bucket = conn.get_bucket(s3_bucket)

        # go through the list of files
        bucket_list = bucket.list()
        for l in bucket_list:
            key_string = str(l.key)
            l.get_contents_to_filename(os.path.join(data_dir, key_string))
        self.print_info('done')

        self.print_info('Computing hashes of new files')
        new_hashes = self.hashes(data_dir, ['courts.json'])
        if new_hashes != old_hashes:
            self.print_info('Hashes differ. Importing the new files')
            self.import_files(data_dir)
        else:
            self.print_info('Same hashes. Not importing.')
        return new_hashes
