# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_auto_20140818_1751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='court',
            name='area',
        ),
        migrations.DeleteModel(
            name='Area',
        ),
    ]
