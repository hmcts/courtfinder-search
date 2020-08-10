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
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('number', models.CharField(max_length=255)),
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
                ('country', models.ForeignKey(to='search.Country', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Court',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('admin_id', models.IntegerField(default=None, null=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('displayed', models.BooleanField(default=False)),
                ('lat', models.FloatField(null=True)),
                ('lon', models.FloatField(null=True)),
                ('number', models.IntegerField(null=True)),
                ('alert', models.CharField(default=None, max_length=4096, null=True)),
                ('directions', models.CharField(default=None, max_length=4096, null=True)),
                ('image_file', models.CharField(default=None, max_length=255, null=True)),
                ('cci_code', models.CharField(default=None, max_length=255, null=True)),
                ('updated_at', models.DateTimeField(default=None, null=True)),
                ('created_at', models.DateTimeField(default=None, null=True)),
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
                ('address_type', models.ForeignKey(to='search.AddressType', on_delete=models.CASCADE)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtAreaOfLaw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area_of_law', models.ForeignKey(to='search.AreaOfLaw', on_delete=models.CASCADE)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
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
        migrations.CreateModel(
            name='CourtContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact', models.ForeignKey(to='search.Contact', on_delete=models.CASCADE)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtCourtType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtFacility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtLocalAuthorityAreaOfLaw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area_of_law', models.ForeignKey(to='search.AreaOfLaw', on_delete=models.CASCADE)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtOpeningTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtPostcode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('postcode', models.CharField(max_length=250)),
                ('court', models.ForeignKey(to='search.Court', on_delete=models.CASCADE)),
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
        migrations.CreateModel(
            name='DataStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_hash', models.CharField(max_length=255)),
                ('last_ingestion_date', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
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
            name='LocalAuthority',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
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
        migrations.CreateModel(
            name='ParkingInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('onsite', models.CharField(default=None, max_length=1024, null=True)),
                ('offsite', models.CharField(default=None, max_length=1024, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Town',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('county', models.ForeignKey(to='search.County', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='courtopeningtime',
            name='opening_time',
            field=models.ForeignKey(to='search.OpeningTime', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtlocalauthorityareaoflaw',
            name='local_authority',
            field=models.ForeignKey(to='search.LocalAuthority', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtfacility',
            name='facility',
            field=models.ForeignKey(to='search.Facility', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtemail',
            name='email',
            field=models.ForeignKey(to='search.Email', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtcourttype',
            name='court_type',
            field=models.ForeignKey(to='search.CourtType', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtattribute',
            name='attribute_type',
            field=models.ForeignKey(to='search.CourtAttributeType', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtattribute',
            name='court',
            field=models.ForeignKey(to='search.Court', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courtaddress',
            name='town',
            field=models.ForeignKey(to='search.Town', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='addresses',
            field=models.ManyToManyField(to='search.AddressType', null=True, through='search.CourtAddress'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='areas_of_law',
            field=models.ManyToManyField(to='search.AreaOfLaw', null=True, through='search.CourtAreaOfLaw'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='attributes',
            field=models.ManyToManyField(to='search.CourtAttributeType', null=True, through='search.CourtAttribute'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='contacts',
            field=models.ManyToManyField(to='search.Contact', null=True, through='search.CourtContact'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='court_types',
            field=models.ManyToManyField(to='search.CourtType', null=True, through='search.CourtCourtType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='emails',
            field=models.ManyToManyField(to='search.Email', null=True, through='search.CourtEmail'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='facilities',
            field=models.ManyToManyField(to='search.Facility', null=True, through='search.CourtFacility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='opening_times',
            field=models.ManyToManyField(to='search.OpeningTime', null=True, through='search.CourtOpeningTime'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='parking',
            field=models.ForeignKey(default=None, to='search.ParkingInfo', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
