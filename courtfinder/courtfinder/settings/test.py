"""Production settings and globals."""

from __future__ import absolute_import
from django.utils.translation import ugettext_lazy as _

from os import environ

from .base import *

DEBUG = True

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


FEATURE_WELSH_ENABLED = True

LANGUAGES = (
    ('en', _('English')),
    ('cy', _('Welsh')),
)