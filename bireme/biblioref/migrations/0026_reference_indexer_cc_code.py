# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0025_auto_20171016_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='indexer_cc_code',
            field=models.CharField(max_length=55, verbose_name='Indexed by', blank=True),
        ),
    ]
