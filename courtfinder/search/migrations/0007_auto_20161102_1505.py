# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0006_auto_20141121_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facility',
            name='description',
            field=models.CharField(max_length=4096, null=True, blank=True),
            preserve_default=True,
        )
    ]
