"""Production settings and globals."""
from __future__ import absolute_import
from .base import *

DEBUG = False
STATIC_ROOT = '/srv/search/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search',
        'USER': 'courtfinder_search',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = '*'

COURTFINDER_ADMIN_HEALTHCHECK = 'https://courttribunalfinder.service.gov.uk/admin/healthcheck.json'
