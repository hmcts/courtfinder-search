# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-06 15:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0033_emergencymessage_message_cy'),
    ]

    operations = [
        migrations.AddField(
            model_name='areaoflaw',
            name='external_link_cy',
            field=models.CharField(blank=True, default=None, max_length=2048, null=True),
        ),
    ]