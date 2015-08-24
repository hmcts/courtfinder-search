# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('search', '0007_areaoflaw_slug'),
    ]
    operations = [
        migrations.CreateModel(
            name='SearchStatistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_search', models.DateTimeField(null=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
