"""Production settings and globals."""

from __future__ import absolute_import

from os import environ

from .base import *

import logging
logging.disable(logging.CRITICAL)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search',
        'USER': 'postgres',
    },
    'temp': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search_tmp',
        'USER': 'postgres',
    }
}

