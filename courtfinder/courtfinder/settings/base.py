"""
Django settings for courtfinder project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import abspath, basename, dirname, join, normpath
from sys import path
from os import environ

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


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '99z2o2nkqlks_#wmbz(&+-_q)c@r_j*3#zeyn)s6pv3iyo_s6i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'moj_template',
    'search',
    'staticpages',
    'courts',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'courtfinder.urls'

WSGI_APPLICATION = 'courtfinder.wsgi.application'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    SITE_ROOT + '/templates',
)

TEMPLATE_CONTEXT_PROCESSORS =  (
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
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    SITE_ROOT + '/assets',
)

# Postcode lookup
MAPIT_BASE_URL = 'http://mapit.mysociety.org/postcode/'

# Email for feedback
FEEDBACK_EMAIL_SENDER = os.environ.get('FEEDBACK_EMAIL_SENDER', 'no-reply@courttribunalfinder.service.gov.uk')
FEEDBACK_EMAIL_RECEIVER = os.environ.get('FEEDBACK_EMAIL_RECEIVER', None)

EMAIL_HOST = os.environ.get('SMTP_HOSTNAME', None)
EMAIL_PORT = 25
EMAIL_HOST_USER = os.environ.get('SMTP_USERNAME', None)
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD', None)
