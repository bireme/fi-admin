# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0017_auto_20190502_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treenumberslistdesc',
            name='tree_number',
            field=models.CharField(max_length=250, verbose_name='Tree number', blank=True),
        ),
    ]
