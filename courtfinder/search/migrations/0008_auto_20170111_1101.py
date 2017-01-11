# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0007_auto_20161102_1505'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='areaoflaw',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='areaoflaw',
            name='external_link',
            field=models.CharField(max_length=2048, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='areaoflaw',
            name='external_link_desc',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
    ]
