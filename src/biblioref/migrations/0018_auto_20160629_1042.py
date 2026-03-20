# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0017_reference_indexed_database'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referencesource',
            name='title_serial',
            field=models.TextField(verbose_name='Title', blank=True),
        ),
    ]
