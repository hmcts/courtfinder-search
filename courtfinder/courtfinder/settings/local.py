"""Development settings and globals."""

from __future__ import absolute_import

from os.path import join, normpath

from .production import *


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

########## END DEBUG CONFIGURATION

SECRET_KEY = "a-secret-key"
