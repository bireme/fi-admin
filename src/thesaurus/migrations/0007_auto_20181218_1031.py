# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0006_auto_20181107_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='code_controller',
            name='thesaurus',
            field=models.CharField(max_length=50, verbose_name='Thesaurus', blank=True),
        ),
        migrations.AddField(
            model_name='thesaurus',
            name='thesaurus_acronym',
            field=models.CharField(max_length=10, verbose_name='Thesaurus acronym', blank=True),
        ),
    ]
