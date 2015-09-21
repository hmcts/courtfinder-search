"""Production settings and globals."""

from __future__ import absolute_import

from os import environ

from .base import *

DEBUG = False
STATIC_ROOT = '/srv/search/static/'

########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'temp_courtfinder_search',
        'USER': 'courtfinder_search',
        'PASSWORD': '123456',
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': '5432',
    }
}
########## END DATABASE CONFIGURATION

ALLOWED_HOSTS = '*'

