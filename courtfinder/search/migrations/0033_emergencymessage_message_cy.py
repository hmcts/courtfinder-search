# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-02 09:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0032_areaoflaw_external_link_desc_cy'),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencymessage',
            name='message_cy',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]