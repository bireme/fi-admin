# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0007_auto_20150921_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='LILACS_indexed',
            field=models.BooleanField(default=True, verbose_name='LILACS indexed?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reference',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (0, 'Pending'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')]),
            preserve_default=True,
        ),
    ]
