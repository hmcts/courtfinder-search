from storages.backends.azure_storage import AzureStorage
from django.conf import settings


class CtfAzureStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_STORAGE_KEY
    expiration_secs = None
    overwrite_files = True


class AzureMediaStorage(CtfAzureStorage):
    azure_container = settings.MEDIA_LOCATION


class AzureStaticStorage(CtfAzureStorage):
    azure_container = settings.STATIC_LOCATION

