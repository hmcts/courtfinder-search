# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_auto_20140822_1038'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_hash', models.CharField(max_length=255)),
                ('last_ingestion_date', models.DateField(auto_now=True, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
