# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-26 16:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0017_merge_20170601_0751'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='magistrate_code',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
