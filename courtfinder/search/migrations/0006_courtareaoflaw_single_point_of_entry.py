# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_auto_20141017_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='courtareaoflaw',
            name='single_point_of_entry',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
