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


LANGUAGES = (
    ('en', _('English')),
    ('cy', _('Welsh')),
)


FEEDBACK_EMAIL_RECEIVER = 'eng_receive@a.com'
WELSH_FEEDBACK_EMAIL_RECEIVER = 'welsh_receive@b.com'

RATELIMIT_LOGIN = False
