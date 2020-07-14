import os


SECRETS_PATH = os.environ.get('SECRETS_PATH', os.path.expanduser('~/kvmnt/ctf/'))


def secrets(key, default=None):
    """ Retrieve variables from mounted azure key value store """
    azure_secret = os.getenv(key)
    if not azure_secret:
        return default

    # <azure-secret:env-cf-key>
    file_name = azure_secret[14:-1]

    try:
        with open(SECRETS_PATH + file_name, 'r') as file:
            value = file.read().strip()
        return value
    except FileNotFoundError as e:
        return default
