"""Production settings and globals."""

from __future__ import absolute_import

from os import environ

from .base import *


########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search',
        'USER': 'courtfinder',
        'PASSWORD': '123456',
        'HOST': os.getenv('DB_HOSTNAME', '127.0.0.1'),
        'PORT': '5432',
    }
}
########## END DATABASE CONFIGURATION

# quieter Raven logger when running tests
LOGGING['handlers']['console'] = {
    'level': 'WARNING',
    'class': 'logging.StreamHandler',
    'formatter': 'simple'
}
LOGGING['loggers']['raven'] = {
    'handlers': ['console'],
    'level': 'WARNING'
}
