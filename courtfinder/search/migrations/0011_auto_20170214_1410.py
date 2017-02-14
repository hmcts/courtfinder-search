# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0010_court_hide_aols'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='defence_leaflet',
            field=models.CharField(default=None, max_length=2500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='info_leaflet',
            field=models.CharField(default=None, max_length=2500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='juror_leaflet',
            field=models.CharField(default=None, max_length=2500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='prosecution_leaflet',
            field=models.CharField(default=None, max_length=2500, null=True),
            preserve_default=True,
        ),
    ]
