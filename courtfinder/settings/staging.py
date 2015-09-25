"""Staging settings and globals."""
from __future__ import absolute_import
from .base import *

DEBUG = False
STATIC_ROOT = '/srv/search/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search',
        'USER': 'courtfinder',
        'PASSWORD': 'C1cwG3P7n2',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = '*'

COURTFINDER_ADMIN_HEALTHCHECK = 'https://courtfinder.is.dsd.io/admin/healthcheck.json'
COURTS_DATA_S3_URL = 'https://s3-eu-west-1.amazonaws.com/courtfinder-json-staging/courts.json'
