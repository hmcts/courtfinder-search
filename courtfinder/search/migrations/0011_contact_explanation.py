# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0010_court_hide_aols'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='explanation',
            field=models.CharField(max_length=85, null=True),
            preserve_default=True,
        ),
    ]
