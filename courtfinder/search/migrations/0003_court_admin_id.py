# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_auto_20140822_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='admin_id',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
    ]
