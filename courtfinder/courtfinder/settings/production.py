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

FEATURE_LEAFLETS_ENABLED = is_enabled('FEATURE_LEAFLETS_ENABLED')

DEFAULT_FILE_STORAGE = 'core.storage.AzureMediaStorage'
STATICFILES_STORAGE = 'core.storage.AzureStaticStorage'

STATIC_LOCATION = "assets"
MEDIA_LOCATION = "media"

AZURE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT')
AZURE_STORAGE_KEY = secrets('AZURE_STORAGE_ACCESS_KEY')

AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'
STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'

COURT_IMAGE_BASE_URL = MEDIA_URL + 'images/'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

OPENCENSUS = {
    'TRACE': {
        'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler(rate=1)',
        'EXPORTER': f'''opencensus.ext.azure.trace_exporter.AzureExporter(
            connection_string="{secrets('APPINSIGHTS_CONNECTION_STRING')}"
        )''',
    }
}


import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)

try:
    logger.addHandler(AzureLogHandler(
        connection_string=f"{secrets('APPINSIGHTS_CONNECTION_STRING')}")
    )

    logger.warning('startup')
except ValueError as e:
    print(f"connection string: {secrets('APPINSIGHTS_CONNECTION_STRING')}, env: {os.getenv('APPINSIGHTS_CONNECTION_STRING')}")
