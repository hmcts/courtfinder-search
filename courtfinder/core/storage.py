from storages.backends.azure_storage import AzureStorage
from django.conf import settings


class AzureMediaStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_STORAGE_KEY
    azure_container = settings.MEDIA_LOCATION
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_STORAGE_KEY
    azure_container = settings.STATIC_LOCATION
    expiration_secs = None
