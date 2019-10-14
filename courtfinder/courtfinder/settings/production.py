"""Production settings and globals."""

from __future__ import absolute_import
from .base import *

DEBUG = False
STATIC_ROOT = '/srv/search/assets/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': secrets('DB_NAME','courtfinder_search'),
        'USER': secrets('DB_USER', 'courtfinder'),
        'PASSWORD': secrets('DB_PASSWORD'),
        'HOST': secrets('DB_HOST', '127.0.0.1'),
        'PORT': secrets('DB_PORT', '5432'),
    },
    '_tmp': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '_tmp',
        'USER': secrets('DB_USER', 'courtfinder'),
        'PASSWORD': secrets('DB_PASSWORD','C1cwG3P7n2'),
        'HOST': secrets('DB_HOST', '127.0.0.1'),
        'PORT': secrets('DB_PORT', '5432'),
    }
}

ALLOWED_HOSTS = '*'

COURTFINDER_ADMIN_HEALTHCHECK_URL = secrets('COURTFINDER_ADMIN_HEALTHCHECK_URL')
COURTS_DATA_S3_URL = 'https://s3-eu-west-1.amazonaws.com/courtfinder-json-production/courts.json'
COURT_IMAGE_BASE_URL = secrets('COURT_IMAGE_BASE_URL', 'https://courtfinder-servicegovuk-production.s3.amazonaws.com/images/')

FEATURE_LEAFLETS_ENABLED = is_enabled('FEATURE_LEAFLETS_ENABLED')
FEATURE_WELSH_ENABLED = True
