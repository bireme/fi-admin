# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0011_identifierconceptlistdesc_historical_annotation'),
    ]

    operations = [
        migrations.AddField(
            model_name='identifierconceptlistqualif',
            name='historical_annotation',
            field=models.TextField(max_length=1500, verbose_name='Historical annotation', blank=True),
        ),
    ]
