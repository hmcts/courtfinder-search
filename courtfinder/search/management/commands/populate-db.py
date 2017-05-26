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
from django.db.utils import IntegrityError, ProgrammingError
from optparse import make_option

from search.models import DataStatus
from search.ingest import Ingest


class Command(BaseCommand):

    logger= None

    def add_arguments(self, parser):
        parser.add_argument('--datadir', default='data',
                            help='Set the data directory containing courts files')
        parser.add_argument('--database', default='default',
                            help='Set the database to import date into')
        parser.add_argument('--load-remote', default=False, action='store_true',
                            help='Load the courts files from remote sources')
        parser.add_argument('--ingest', default=False, action='store_true',
                            help='Ingest the local court files')
        parser.add_argument('--sys-exit', default=False, action='store_true',
                            help='Make the script use sys exits')

    
    def __init__(self):
        super(Command, self).__init__()
        self.setup_logging()


    def handle(self, *args, **options):
        """
        Handle the loading of file data into the application. There
        are a number of different outcomes depending on which arguments
        if any are supplied.

        * 'no arguments' - firstly 'load-remote' is called, then,
        if and only if the files have changed, 'ingest' is called.
        * 'load-remote' only - courts.json is fetched from the remote store,
        but is not ingested.
        * 'ingest' only - the local copy of courts.json is ingested
        * 'load-remote' and 'ingest' - The remote courts.json is fetched and
        ingested no matter if its changed or not

        Multiple database support is available through the passing of the database
        parameter to specify which databse to load data into.
        """
        courts_files = ["courts.json"]
        local_dir = options['datadir']
        remote_dir = ""
        
        # Store the current hash
        old_hash = self.hashes(local_dir, courts_files)

        do_load_remote = False
        do_ingest = False
        ingest_if_unchanged = False
        exit_if_unchanged = False

        # If no commands are specified then default to the previous behaviour
        if not options['load_remote'] and not options['ingest']:
            self.logger.info("handle: No commands specified, running load-remote and ingest if files change...")
            do_load_remote = True
            do_ingest = True
            ingest_if_unchanged = False 
        else:
            if options['load_remote']:
                do_load_remote = True
                exit_if_unchanged = True
            if options['ingest']:
                do_ingest = True
                ingest_if_unchanged = True

        if do_load_remote:
            self.logger.info("handle: Loading remote files...")
            load_remote_files_success = self.load_remote_files(local_dir,
                                                               remote_dir,
                                                               courts_files)
            if not load_remote_files_success:
                self.logger.critical("handle: Failed to load remote files, exiting")
                sys.exit(1)

        files_changed = self.hashes(local_dir, courts_files) != old_hash

        # If the files have not changed, and we have not specifically
        # asked for the files to be ingested,then exit
        if exit_if_unchanged and not files_changed:
            self.logger.info("handle: Loaded remote files are unchanged...")
            if (options['sys_exit']):
                sys.exit(200)
            else:
                return

        if do_ingest:
            if files_changed or ingest_if_unchanged:
                self.logger.info("handle: Ingesting files...")
                success = self.import_files(local_dir, courts_files, options['database'])
                if not success:
                    self.logger.critical('handle: Importing the courts data was unsuccessful')
                    if (options['sys_exit']):
                        sys.exit(1)
                if (options['sys_exit']):
                    sys.exit(0)
                else:
                    return
            else:
                self.logger.info("handle: Loaded remote files are unchanged...")
                if (options['sys_exit']):
                    sys.exit(0)
                else:
                    return

        

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
        
        Return:
            (bool): True if remote files were successfully loaded, false otherwise
        """
        # determine where the json files are
        s3_bucket = os.environ.get('S3_BUCKET', None)
        if not s3_bucket:
            self.logger.critical('handle: No S3_BUCKET environment variable found')
            return False
        
        bucket_name = s3_bucket.split('.')[0]
        self.logger.info('handle: Found S3_BUCKET environment variable {}'.format(bucket_name))
        local_dir = "data"
        remote_dir = ""
        s3_success = self.handle_s3(bucket_name,
                                   local_dir=local_dir,
                                   remote_dir=remote_dir,
                                   files=files)
        return s3_success

    def import_files(self,
                     local_dir,
                     filenames,
                     database_name="default"):
        """
        Imports the set of files from the specified directory into
        the application

        Args:
            local_dir(string): The directory containing the files
            filenames(list): List of files to import
            database_name(string): The database to import the data into

        Returns:
            (bool): True if ingestion was successful, False otherwise
        """
        for filename in filenames:
            courts_data_path = os.path.join(local_dir, filename)
            with open(courts_data_path, 'r') as courtsfile:
                self.logger.info('import_files: Importing file {}/{}'.format(local_dir, filename))
                courts = json.load(courtsfile)
                courtsfile.close()
                # Import the data into the application
                try:
                    Ingest.courts(courts['courts'], database_name=database_name)
                    Ingest.emergency_message(courts['emergency_message'], database_name=database_name)
                except (IntegrityError, ProgrammingError) as e:
                    error_name = e.__class__.__name__
                    self.logger.critical("import_files: There was a django '{}' error ingesting the courts data, '{}'"
                                         .format(error_name, e.message))
                    return False
        # Set the ingestion status
        DataStatus.objects.db_manager(database_name).create(data_hash=''.join(self.hashes(local_dir, filenames)))
        return True

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

        Return:
            (bool): True if files downloaded successfully, false otherwise
        """
        old_hashes = self.hashes(local_dir, files)
        s3 = boto3.resource('s3')
        found_files = []
        for file in files:
            local_path = os.path.join(local_dir, file)
            remote_path = os.path.join(remote_dir, file)
            self.logger.info("handle_s3: Attempting download of {} to {} "
                        "from bucket {}, ".format(remote_path, local_path, bucket_name))

            try:
                s3.meta.client.download_file(bucket_name, remote_path, local_path)
            except botocore.exceptions.ClientError as e:
                # Only catch the non-existing error
                error_code = int(e.response['Error']['Code'])
                if error_code == 404:
                    self.logger.critical("handle_s3: File {} not found in bucket {}"
                                         .format(file, bucket_name))
                    return False

        return True


    def setup_logging(self,
                      log_level='INFO',
                      log_format='json',
                      log_file=None):
        """
        Setup the logging
        """
        if log_format == 'json':
            logging_format_str = '{"timestamp": "%(asctime)s","name": "%(name)s", "level": "%(levelname)s", "level_no": %(levelno)i, "message": "%(message)s"}'
        else:
            logging_format_str = '%(asctime)s %(name)s: %(levelname)s: %(message)s'

        logging.basicConfig(
            format=logging_format_str,
            filename=log_file,
            level=log_level)
        # Set up the logging
        logging.basicConfig(format=logging_format_str,
                            level=logging.getLevelName(log_level))
        self.logger = logging.getLogger("courtfinder-search::populate-db.py:")
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger('boto').setLevel(logging.CRITICAL)
