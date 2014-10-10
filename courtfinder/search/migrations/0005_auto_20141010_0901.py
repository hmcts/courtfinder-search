# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_auto_20140925_1441'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourtFacilities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('court', models.ForeignKey(to='search.Court')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtOpeningTimes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('court', models.ForeignKey(to='search.Court')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=4096)),
                ('image', models.CharField(max_length=255)),
                ('image_description', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpeningTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=1024)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='courtopeningtimes',
            name='opening_time',
            field=models.ForeignKey(to='search.OpeningTime'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtfacilities',
            name='facility',
            field=models.ForeignKey(to='search.Facility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='alert',
            field=models.CharField(default=None, max_length=4096, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='facilities',
            field=models.ManyToManyField(to='search.Facility', null=True, through='search.CourtFacilities'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='image_file',
            field=models.CharField(default=None, max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='opening_times',
            field=models.ManyToManyField(to='search.OpeningTime', null=True, through='search.CourtOpeningTimes'),
            preserve_default=True,
        ),
    ]
