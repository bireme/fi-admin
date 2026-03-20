# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0026_reference_indexer_cc_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='referencesource',
            name='doi_number',
            field=models.CharField(max_length=150, verbose_name='DOI number', blank=True),
        ),
    ]
