# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_courtareaoflaw_single_point_of_entry'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkinginfo',
            name='blue_badge',
            field=models.CharField(default=None, max_length=1024, null=True),
            preserve_default=True,
        ),
    ]
