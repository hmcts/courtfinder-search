# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0012_auto_20170303_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='in_leaflet',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
