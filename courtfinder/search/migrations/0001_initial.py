# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AddressType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AreaOfLaw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('country', models.ForeignKey(to='search.Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Court',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('number', models.IntegerField(null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('displayed', models.BooleanField(default=False)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.TextField()),
                ('postcode', models.CharField(max_length=255)),
                ('address_type', models.ForeignKey(to='search.AddressType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='court',
            name='addresses',
            field=models.ManyToManyField(to='search.AddressType', null=True, through='search.CourtAddress'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtaddress',
            name='court',
            field=models.ForeignKey(to='search.Court'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CourtAreasOfLaw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area_of_law', models.ForeignKey(to='search.AreaOfLaw')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='court',
            name='areas_of_law',
            field=models.ManyToManyField(to='search.AreaOfLaw', null=True, through='search.CourtAreasOfLaw'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtareasoflaw',
            name='court',
            field=models.ForeignKey(to='search.Court'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CourtAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('court', models.ForeignKey(to='search.Court')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtAttributeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='courtattribute',
            name='attribute_type',
            field=models.ForeignKey(to='search.CourtAttributeType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='attributes',
            field=models.ManyToManyField(to='search.CourtAttributeType', null=True, through='search.CourtAttribute'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CourtContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=255)),
                ('contact_type', models.ForeignKey(to='search.ContactType')),
                ('court', models.ForeignKey(to='search.Court')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtCourtTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('court', models.ForeignKey(to='search.Court')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='courtcourttypes',
            name='court_type',
            field=models.ForeignKey(to='search.CourtType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='court_types',
            field=models.ManyToManyField(to='search.CourtType', null=True, through='search.CourtCourtTypes'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Town',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('county', models.ForeignKey(to='search.County')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='courtaddress',
            name='town',
            field=models.ForeignKey(to='search.Town'),
            preserve_default=True,
        ),
    ]
