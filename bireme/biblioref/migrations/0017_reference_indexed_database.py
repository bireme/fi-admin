# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_auto_20160627_1750'),
        ('biblioref', '0016_auto_20160610_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='indexed_database',
            field=models.ManyToManyField(to='database.Database', verbose_name='Indexed in', blank=True),
        ),
    ]
