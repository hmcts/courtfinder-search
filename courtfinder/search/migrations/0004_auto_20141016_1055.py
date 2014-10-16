# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_datastatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datastatus',
            name='last_ingestion_date',
            field=models.DateTimeField(auto_now=True, auto_now_add=True),
        ),
    ]
