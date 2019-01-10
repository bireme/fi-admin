# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0008_code_controller_term'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thesaurus',
            name='thesaurus_acronym',
            field=models.CharField(max_length=3, verbose_name='Thesaurus acronym', blank=True),
        ),
    ]
