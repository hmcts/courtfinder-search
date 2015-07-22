# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_contact_sort_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='county',
            name='country',
        ),
        migrations.DeleteModel(
            name='Country',
        ),
        migrations.AlterField(
            model_name='town',
            name='county',
            field=models.CharField(max_length=255),
        ),
        migrations.DeleteModel(
            name='County',
        ),
    ]
