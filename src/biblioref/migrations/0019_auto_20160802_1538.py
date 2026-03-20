# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0018_auto_20160629_1042'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referencesource',
            name='doi_number',
        ),
        migrations.AddField(
            model_name='referenceanalytic',
            name='doi_number',
            field=models.CharField(max_length=150, verbose_name='DOI number', blank=True),
        ),
        migrations.AlterField(
            model_name='reference',
            name='LILACS_indexed',
            field=models.BooleanField(default=True, verbose_name='Validate using LILACS methodology'),
        ),
    ]
