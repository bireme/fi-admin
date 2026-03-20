# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0012_identifierconceptlistqualif_historical_annotation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treenumberslistdesc',
            name='tree_number',
            field=models.CharField(unique=True, max_length=250, verbose_name='Tree number', blank=True),
        ),
    ]
