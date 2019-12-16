"""
Django settings for courtfinder project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import abspath, basename, dirname, join, normpath, exists
from sys import path
from django.utils.translation import ugettext_lazy as _
from . import secrets
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(secrets('SENTRY_URL', None), integrations=[DjangoIntegration()])

# Log handler for LogEntries
from logentries import LogentriesHandler

def is_enabled(name, default=False):
    default = 'yes' if default else 'no'
    return os.getenv(name, default).lower() in ['enabled', 'yes', 'true', '1']

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Project root:
PROJECT_ROOT = dirname(SITE_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION

SECRET_KEY = secrets('DJANGO_SECRET_KEY', '99z2o2nkqlks_#wmbz(&+-_q)c@r_j*3#zeyn)s6pv3iyo_s6i')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = '*'


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.messages',
    'core',
    'search',
    'staticpages',
    'courts',
    'healthcheck',
    'admin',
    'storages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.RequestLoggingMiddleware',
    'admin.middleware.RequireLoginMiddleware',
    'admin.middleware.ForceAdminEnglishMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'opencensus.ext.django.middleware.OpencensusMiddleware',
    'ratelimit.middleware.RatelimitMiddleware',
)

RATELIMIT_VIEW = 'admin.auth.limited'

ROOT_URLCONF = 'courtfinder.urls'

WSGI_APPLICATION = 'courtfinder.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            SITE_ROOT + '/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                'django.template.context_processors.request',
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "courtfinder.context_processors.globals",
            ]
        }
    }
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'courtfinder_search',
        'USER': 'courtfinder',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
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

SESSION_COOKIE_PATH = '/staff'
SESSION_COOKIE_AGE = 60*60
SESSION_SAVE_EVERY_REQUEST = True

LOGIN_REDIRECT_URL = 'admin:courts'
LOGIN_URL = 'admin:login'

CSRF_COOKIE_HTTPONLY = True

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalisation
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('cy', _('Welsh')),
)

LOCALE_PATHS = (
    SITE_ROOT + '/locale',
)

# Security middleware
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

STATIC_URL = '/assets/'

STATICFILES_DIRS = (
    SITE_ROOT + '/assets',
)

# Postcode lookup
MAPIT_BASE_URL = 'https://mapit.mysociety.org/postcode/'
MAPTI_API_KEY = secrets('MAPIT_API_KEY', None)

# Email for feedback
FEEDBACK_EMAIL_SENDER = os.environ.get('FEEDBACK_EMAIL_SENDER', 'no-reply@courttribunalfinder.service.gov.uk')
FEEDBACK_EMAIL_RECEIVER = secrets('FEEDBACK_EMAIL_RECEIVER', None)
WELSH_FEEDBACK_EMAIL_RECEIVER = secrets('WELSH_FEEDBACK_EMAIL_RECEIVER', None)

EMAIL_HOST = os.environ.get('SMTP_HOSTNAME', None)
EMAIL_PORT = os.environ.get('SMTP_PORT', None)
EMAIL_HOST_USER = secrets('SMTP_USERNAME', None)
EMAIL_HOST_PASSWORD = secrets('SMTP_PASSWORD', None)
EMAIL_USE_TLS = False

APP_S3_BUCKET = secrets('APP_S3_BUCKET', '')
AWS_ACCESS_KEY_ID = secrets('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = secrets('AWS_SECRET_ACCESS_KEY', '')


AUTODISCOVER_HEALTHCHECKS = True
COURTFINDER_ADMIN_HEALTHCHECK_URL = ''
COURTS_DATA_S3_URL = ''
COURT_IMAGE_BASE_URL = ''

RATELIMIT_LOGIN = True
RATELIMIT_CACHE_BACKEND = 'courtfinder.brake_config.ELBBrake'

FEATURE_LEAFLETS_ENABLED = False

try:
    from .local import *
except ImportError:
    pass
