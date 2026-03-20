# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0016_auto_20190429_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='termlistqualif',
            name='term_string',
            field=models.CharField(max_length=250, verbose_name='String'),
        ),
    ]
