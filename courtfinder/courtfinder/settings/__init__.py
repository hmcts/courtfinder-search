import os


SECRETS_PATH = os.environ.get('SECRETS_PATH', os.path.expanduser('~/kvmnt/ctf/'))


def secrets(key, default=None):
    """ Retrieve variables from mounted azure key value store """
    try:
        with open(SECRETS_PATH + key, 'r') as file:
            value = file.read().strip()
        return value
    except FileNotFoundError as e:
        return default
