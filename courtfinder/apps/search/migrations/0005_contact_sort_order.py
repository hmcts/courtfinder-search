# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_parkinginfo_blue_badge'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='sort_order',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
    ]
