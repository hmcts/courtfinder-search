# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0009_court_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='hide_aols',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
