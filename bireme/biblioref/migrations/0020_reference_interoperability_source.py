# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0019_auto_20160802_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='interoperability_source',
            field=models.CharField(max_length=100, verbose_name='Interoperability source', blank=True),
        ),
    ]
