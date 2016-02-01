"""
Django settings for courtfinder project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import abspath, basename, dirname, join
from sys import path, stdout

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Project root:
PROJECT_ROOT = SITE_ROOT

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
path.append(join(DJANGO_ROOT, 'apps'))
########## END PATH CONFIGURATION


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '99z2o2nkqlks_#wmbz(&+-_q)c@r_j*3#zeyn)s6pv3iyo_s6i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'moj_template',
    'healthcheck',
    'search',
    'staticpages',
    'courts',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'courtfinder.middleware.RequestLoggingMiddleware',
)

ROOT_URLCONF = 'courtfinder.urls'

WSGI_APPLICATION = 'courtfinder.wsgi.application'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    DJANGO_ROOT + '/templates',
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
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': '5432',
    },
    'temp': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search_tmp',
        'USER': 'courtfinder',
        'PASSWORD': 'C1cwG3P7n2',
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
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
STATIC_URL = '/assets/'

STATICFILES_DIRS = (
    DJANGO_ROOT + '/assets',
)

# Postcode lookup
MAPIT_BASE_URL = 'http://mapit.mysociety.org/postcode/'
POSTCODEINFO_API_URL = os.environ.get('POSTCODEINFO_API_URL')
POSTCODEINFO_AUTH_TOKEN = os.environ.get('POSTCODEINFO_API_TOKEN')
POSTCODEINFO_TIMEOUT = os.environ.get('POSTCODEINFO_API_TIMEOUT')

# Email for feedback
FEEDBACK_EMAIL_SENDER = os.environ.get('FEEDBACK_EMAIL_SENDER', 'no-reply@courttribunalfinder.service.gov.uk')
FEEDBACK_EMAIL_RECEIVER = os.environ.get('FEEDBACK_EMAIL_RECEIVER', None)

EMAIL_HOST = os.environ.get('SMTP_HOSTNAME', None)
EMAIL_PORT = os.environ.get('SMTP_PORT', None)
EMAIL_HOST_USER = os.environ.get('SMTP_USERNAME', None)
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD', None)
EMAIL_USE_TLS = False

# Set your DSN value
RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_URL', None),
}

# Add raven to the list of installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)

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
        'log-stdout-debug-simple': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': stdout,
        },
        'log-stdout-debug-noformat': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'no-format',
            'stream': stdout,
        },
        'log-stdout-error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': stdout,
        },
    },
    'loggers': {
        'search.error': {
            'handlers': ['log-stdout-error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search.mapit': {
            'handlers': ['log-stdout-error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search.la': {
            'handlers': ['log-stdout-error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search.aol': {
            'handlers': ['log-stdout-error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search.method': {
            'handlers': ['log-stdout-debug-simple'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'courtfinder.requests': {
            'handlers': ['log-stdout-debug-noformat'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

AUTODISCOVER_HEALTHCHECKS = True
COURTFINDER_ADMIN_HEALTHCHECK_URL = ''
COURTS_DATA_S3_URL = ''

try:
    from .local import *
except ImportError:
    pass
