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
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
########## END DATABASE CONFIGURATION

ALLOWED_HOSTS = '*'

# Set your DSN value
RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_URL', None),
}

# Add raven to the list of installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)
