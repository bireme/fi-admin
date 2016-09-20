# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0002_auto_20160913_1639'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actrelationship',
            name='act_date',
        ),
        migrations.AddField(
            model_name='actrelationship',
            name='denomination',
            field=models.CharField(max_length=255, verbose_name='Denomination', blank=True),
        ),
        migrations.AddField(
            model_name='actrelationship',
            name='issue_date',
            field=models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Issue date', blank=True),
        ),
    ]
