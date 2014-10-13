# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import abspath, basename, dirname, join, normpath
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, migrations


def enable_earthdistance(apps, schema_editor):
  schema_editor.execute('CREATE EXTENSION IF NOT EXISTS cube')
  schema_editor.execute('CREATE EXTENSION IF NOT EXISTS earthdistance')

class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
      migrations.RunPython(enable_earthdistance),
    ]
