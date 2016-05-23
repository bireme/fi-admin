# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0002_auto_20150929_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='titlevariance',
            name='initial_number',
            field=models.CharField(max_length=55, verbose_name='Initial number', blank=True),
        ),
        migrations.AddField(
            model_name='titlevariance',
            name='initial_volume',
            field=models.CharField(max_length=55, verbose_name='Initial volume', blank=True),
        ),
        migrations.AlterField(
            model_name='titlevariance',
            name='type',
            field=models.CharField(blank=True, max_length=55, verbose_name='Type', choices=[(b'230', 'Parallel title'), (b'235', 'Shortened parallel title'), (b'240', 'Other title forms')]),
        ),
    ]
