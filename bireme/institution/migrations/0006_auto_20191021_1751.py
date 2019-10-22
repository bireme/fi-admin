# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0005_auto_20190731_1729'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactphone',
            name='country_code',
        ),
        migrations.AddField(
            model_name='contactphone',
            name='country_area_code',
            field=models.CharField(max_length=20, verbose_name='Country/Area code', blank=True),
        ),
    ]
