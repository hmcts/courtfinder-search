# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0015_facility_image_file_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='courtopeningtime',
            name='sort',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
