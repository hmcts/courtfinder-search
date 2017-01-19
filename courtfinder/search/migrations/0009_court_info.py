# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0008_auto_20170111_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='info',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
