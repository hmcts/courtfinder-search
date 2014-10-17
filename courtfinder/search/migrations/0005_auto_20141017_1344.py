# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_auto_20141016_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='cci_code',
            field=models.CharField(default=None, max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='created_at',
            field=models.DateTimeField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='updated_at',
            field=models.DateTimeField(default=None, null=True),
            preserve_default=True,
        ),
    ]
