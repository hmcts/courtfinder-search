"""Production settings and globals."""

from __future__ import absolute_import
from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME','courtfinder_search'),
        'USER': os.getenv('DB_USER', 'courtfinder'),
        'PASSWORD': secrets('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

ALLOWED_HOSTS = '*'

COURTS_DATA_S3_URL = 'https://s3-eu-west-1.amazonaws.com/courtfinder-json-production/courts.json'
COURT_IMAGE_BASE_URL = os.getenv('COURT_IMAGE_BASE_URL', 'https://courtfinder-servicegovuk-production.s3.amazonaws.com/images/')

FEATURE_LEAFLETS_ENABLED = is_enabled('FEATURE_LEAFLETS_ENABLED')
FEATURE_WELSH_ENABLED = True

DEFAULT_FILE_STORAGE = 'core.storage.AzureMediaStorage'
STATICFILES_STORAGE = 'core.storage.AzureStaticStorage'

STATIC_LOCATION = "static"
MEDIA_LOCATION = "media"

AZURE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT')
AZURE_STORAGE_KEY = os.getenv('AZURE_STORAGE_ACCESS_KEY')

AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'
STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
