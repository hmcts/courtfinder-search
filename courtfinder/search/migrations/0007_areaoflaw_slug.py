# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from django.utils.text import slugify


def generate_fake_slugs(apps, schema_editor):
    AreaOfLaw = apps.get_model('search', 'AreaOfLaw')
    for aol in AreaOfLaw.objects.all():
        aol.slug = slugify(aol.name)
        aol.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('search', '0006_auto_20141121_1653'),
    ]
    operations = [
        migrations.AddField(
            model_name='areaoflaw',
            name='slug',
            field=models.SlugField(default='temp', max_length=255),
            preserve_default=False,
        ),
        migrations.RunPython(generate_fake_slugs, noop),
        migrations.AlterField(
            model_name='areaoflaw',
            name='slug',
            field=models.SlugField(unique=True, max_length=255),
            preserve_default=True,
        ),
    ]
