# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_contact_sort_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='localauthority',
            name='gss_code',
            field=models.CharField(max_length=16, null=True),
            preserve_default=True,
        ),
    ]
