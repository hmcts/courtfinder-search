# -*- encoding: utf-8 -*-
"""
Django settings for courtfinder project.
"""

import os
from os.path import abspath, dirname, join
import sys


# PATH vars
def here(*args):
    return join(abspath(dirname(__file__)), *args)


PROJECT_ROOT = here('..')


def root(*args):
    return join(abspath(PROJECT_ROOT), *args)


APPS_ROOT = root('apps')
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, APPS_ROOT)

SECRET_KEY = '99z2o2nkqlks_#wmbz(&+-_q)c@r_j*3#zeyn)s6pv3iyo_s6i'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')


INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'moj_template',
    'core',
    'healthcheck',
    'search',
    'staticpages',
    'courts',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RequestLoggingMiddleware',
)

ROOT_URLCONF = 'courtfinder.urls'

WSGI_APPLICATION = 'courtfinder.wsgi.application'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    root('templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    'django.core.context_processors.request',
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.contrib.auth.context_processors.auth",
    "courtfinder.context_processors.globals",
)

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search',
        'USER': 'courtfinder',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Internationalisation
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files
STATIC_ROOT = root('static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    root('assets'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Postcode lookup
MAPIT_BASE_URL = 'http://mapit.mysociety.org/postcode/'

# Email for feedback
FEEDBACK_EMAIL_SENDER = os.environ.get(
    'FEEDBACK_EMAIL_SENDER', 'no-reply@courttribunalfinder.service.gov.uk')
FEEDBACK_EMAIL_RECEIVER = os.environ.get('FEEDBACK_EMAIL_RECEIVER')

EMAIL_HOST = os.environ.get('SMTP_HOSTNAME')
EMAIL_PORT = os.environ.get('SMTP_PORT')
EMAIL_HOST_USER = os.environ.get('SMTP_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_USE_TLS = False

# Set your DSN value
RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_URL'),
}

# Add raven to the list of installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)

# Ensure logging directory is created
LOGPATH = root('../logs')
if not os.path.exists(LOGPATH):
    os.makedirs(LOGPATH)


def log_file(filename):
    return join(LOGPATH, filename)


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(message)s'
        },
        'no-format': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'error-file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename':  log_file('errors.log'),
        },
        'missed-las-file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': log_file('missed-las.log'),
        },
        'missed-aols-file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': log_file('missed-aols.log'),
        },
        'mapit-file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': log_file('mapit.log'),
        },
        'search-method-file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': log_file('search-method.log'),
        },
        'courtfinder-requests-file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'no-format',
            'filename': log_file('requests.log'),
        }
    },
    'loggers': {
        'search.error': {
            'handlers': ['error-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search.mapit': {
            'handlers': ['mapit-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search.la': {
            'handlers': ['missed-las-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search.aol': {
            'handlers': ['missed-aols-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search.method': {
            'handlers': ['search-method-file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'courtfinder.requests': {
            'handlers': ['courtfinder-requests-file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

COURTFINDER_ADMIN_HEALTHCHECK = ''
COURTS_DATA_S3_URL = ''

# local.py overrides all the common settings
try:
    from .local import *
except ImportError:
    pass
