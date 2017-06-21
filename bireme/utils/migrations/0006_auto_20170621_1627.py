# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0005_country_la_caribbean'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auxcode',
            name='field',
            field=models.CharField(max_length=50, verbose_name='Field name'),
        ),
    ]
