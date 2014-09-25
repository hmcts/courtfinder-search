# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_court_admin_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='court',
            name='lat',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='court',
            name='lon',
            field=models.FloatField(null=True),
        ),
    ]
