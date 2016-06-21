"""Staging settings and globals."""

from __future__ import absolute_import

from os import environ

from .base import *

COURTFINDER_ADMIN_HEALTHCHECK_URL = 'https://courtfinder.is.dsd.io/admin/healthcheck.json'
COURTS_DATA_S3_URL = 'https://s3-eu-west-1.amazonaws.com/courtfinder-json-staging/courts.json'
