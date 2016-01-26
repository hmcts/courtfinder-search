# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import hashlib
import logging
import sys

import boto3
from boto3.s3.transfer import S3Transfer
import botocore
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option

from search.models import DataStatus
from search.ingest import Ingest

# Set up the logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s')
logger = logging.getLogger("populate-db")
logging.getLogger("requests").setLevel(logging.WARNING)


class Command(BaseCommand):

    # Add some custom options
    option_list = BaseCommand.option_list + (
        make_option('--load-remote',
            action='store_true',
            dest='load-remote',
            default=False,
            help='Load the courts files from remote sources'),
        make_option('--ingest',
            action='store_true',
            dest='ingest',
            default=False,
            help='Ingest the local court files')
    )

    def handle(self, *args, **options):
        """
        Handle the loading of file data into the application
        """
        courts_files = ["courts.json"]
        local_dir = "data"
        remote_dir = ""
        files_changed = False
        exit_code = 0
        
        # If no commands are specified then default to the previous behaviour
        if not options['load-remote'] and not options['ingest']:
            logger.info("handle: No commands specified, running load-remote and ingest...")
            options['load-remote'] = True
            options['ingest'] = True

        if options['load-remote']:
            files_changed = self.load_remote_files(local_dir,
                                   remote_dir,
                                   courts_files
                                   )
            # If the files have not changed, and we have not specifically
            # asked for the files to be ingested,then exit
            if not files_changed and not options['ingest']:
                logger.error("handle: Loaded remote files are unchanged")
                sys.exit(1)
            
        if options['ingest']:
            self.import_files(local_dir, courts_files)
            sys.exit(0)

        sys.exit(0)

    def load_remote_files(self,
                          local_dir,
                          remote_dir,
                          files):
        """
        Load court files from a remote location into the local
        directory

        Args:
            local_dir(string): The local directory to import to
            remote_dir(string): The remote directory to import from
            filenames(list): List of files to import

        Returns:
            changed(bool): True if the files loaded are different to 
                the files previously on the local dir
        """
        # determine where the json files are
        changed = False
        s3_bucket = os.environ.get('S3_BUCKET', None)
        if s3_bucket:
            bucket_name = s3_bucket.split('.')[0]
            logger.info('handle: Found S3_BUCKET environment variable {}'.format(bucket_name))
            local_dir = "data"
            remote_dir = ""
            found_files, changed = self.handle_s3(bucket_name,
                                        local_dir=local_dir,
                                        remote_dir=remote_dir,
                                        files=files)
        return changed

    def import_files(self, local_dir, filenames):
        """
        Imports the set of files from the specified directory into
        the application

        Args:
            local_dir(string): The directory containing the files
            filenames(list): List of files to import
        """
        for filename in filenames:
            courts_data_path = os.path.join(local_dir, filename)
            with open(courts_data_path, 'r') as courtsfile:
                logger.info('import_files: Importing file {}/{}'.format(local_dir, filename))
                courts = json.load(courtsfile)
                courtsfile.close()
                # Import the data into the application
                Ingest.courts(courts)

    @classmethod
    def hashes(cls, dir_path, filenames):
        """
        Generate a list of hashes of the specified
        list of files in the directory

        Args:
            data_dir(string): The directory containing the files
            filenames(list): List of files to import

        Returns:
            (list): List of hashes of the files
        """ 
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


    def handle_s3(self,
                  bucket_name,
                  local_dir,
                  remote_dir,
                  files):
        """
        Handle the importing of s3 files

        Args:
            bucket_name: The name of the s3 bucket to import from
            local_dir(string): The local directory to import to
            remote_dir(string): The remote directory to import from
            filenames(list): List of files to import

        Returns:
            found_files(list): All the hashes of the files imported
            changed(bool): True if the files hashes have changed,
                False otherwise
        """
        old_hashes = self.hashes(local_dir, files)
        s3 = boto3.resource('s3')
        found_files = []
        for file in files:
            local_path = os.path.join(local_dir, file)
            remote_path = os.path.join(remote_dir, file)
            logger.info("handle_s3: Attempting download of {} to {} "
                        "from bucket {}, ".format(remote_path, local_path, bucket_name))
            
            try:
                s3.meta.client.download_file(bucket_name, remote_path, local_path)
                found_files.append(file)
            except botocore.exceptions.ClientError as e:
                # Only catch the non-existing error
                error_code = int(e.response['Error']['Code'])
                if error_code == 404:
                    logger.critical("handle_s3: File {} not found in bucket {}, "
                                   "exiting...".format(file, bucket_name))
                                    
                            
        # If we found any files, then create hashes
        if len(found_files) > 0:
            logger.info("handle_s3: Computing hashes of new files")
            new_hashes = self.hashes(local_dir, found_files)
            if old_hashes == '' or new_hashes != old_hashes:
                logger.info("handle_s3: Hashes differ. Importing the new files")
                DataStatus.objects.create(data_hash=''.join(new_hashes))
                return found_files, True
            else:
                logger.info("handle_s3: Hashes are unchanged.")
                return found_files, False
        else:
            return found_files, False
