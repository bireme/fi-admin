# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='database',
            name='cc_index',
            field=models.CharField(max_length=55, verbose_name='Cooperative Center index', blank=True),
        ),
    ]
