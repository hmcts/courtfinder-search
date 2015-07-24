"""Production settings and globals."""

from __future__ import absolute_import

from .base import *
import os

DEBUG = False
STATIC_ROOT = '/srv/search/static/'

########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search',
        'USER': 'courtfinder_search',
        'PASSWORD': '123456',
        'HOST': os.getenv('DB_HOSTNAME', '127.0.0.1'),
        'PORT': '5432',
    }
}
########## END DATABASE CONFIGURATION

ALLOWED_HOSTS = '*'

