# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0013_auto_20190301_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treenumberslistdesc',
            name='tree_number',
            field=models.CharField(unique=True, max_length=250, verbose_name='Tree number'),
        ),
    ]
