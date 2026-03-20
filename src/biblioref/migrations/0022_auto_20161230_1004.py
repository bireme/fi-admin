# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0021_auto_20161026_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='indexed_database',
            field=models.ManyToManyField(to='database.Database', verbose_name='Indexed in'),
        ),
        migrations.AlterField(
            model_name='reference',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-2, 'Submission'), (-1, 'Draft'), (0, 'Inprocess'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')]),
        ),
    ]
