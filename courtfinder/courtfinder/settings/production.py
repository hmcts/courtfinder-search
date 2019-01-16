"""Production settings and globals."""

from __future__ import absolute_import
from django.utils.translation import ugettext_lazy as _
from .base import *
import os

DEBUG = False
STATIC_ROOT = '/srv/search/assets/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME','courtfinder_search'),
        'USER': os.getenv('DB_USER', 'courtfinder'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    },
    '_tmp': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '_tmp',
        'USER': os.getenv('DB_USER', 'courtfinder'),
        'PASSWORD': os.getenv('DB_PASSWORD','C1cwG3P7n2'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

ALLOWED_HOSTS = '*'

COURTFINDER_ADMIN_HEALTHCHECK_URL = os.getenv('COURTFINDER_ADMIN_HEALTHCHECK_URL')
COURTS_DATA_S3_URL = 'https://s3-eu-west-1.amazonaws.com/courtfinder-json-production/courts.json'
COURT_IMAGE_BASE_URL = os.getenv('COURT_IMAGE_BASE_URL', 'https://courtfinder-servicegovuk-production.s3.amazonaws.com/images/')

FEATURE_LEAFLETS_ENABLED = is_enabled('FEATURE_LEAFLETS_ENABLED')
FEATURE_WELSH_ENABLED = is_enabled('FEATURE_WELSH_ENABLED')

if FEATURE_WELSH_ENABLED:
    LANGUAGES = (
        ('en', _('English')),
        ('cy', _('Welsh')),
    )