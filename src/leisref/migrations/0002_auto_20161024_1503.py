# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actrelationtypelocal',
            name='name',
        ),
        migrations.AddField(
            model_name='actrelationtypelocal',
            name='label_past',
            field=models.CharField(default='', max_length=155, verbose_name='Past form'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actrelationtypelocal',
            name='label_present',
            field=models.CharField(default='', max_length=155, verbose_name='Present tense form'),
            preserve_default=False,
        ),
    ]
