# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0022_auto_20161230_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='indexed_database',
            field=models.ManyToManyField(to='database.Database', verbose_name='Indexed in', blank=True),
        ),
        migrations.AlterField(
            model_name='reference',
            name='transfer_date_to_database',
            field=models.CharField(verbose_name='Transfer date do database', max_length=20, editable=False, blank=True),
        ),
    ]
