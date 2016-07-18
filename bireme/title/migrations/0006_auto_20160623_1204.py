# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0005_auto_20160530_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexrange',
            name='copy',
            field=models.CharField(blank=True, max_length=55, verbose_name='Copy', choices=[(1, 'MEDLINE Index'), (2, 'MEDLINE Record')]),
        ),
        migrations.AddField(
            model_name='indexrange',
            name='distribute',
            field=models.BooleanField(default=False, verbose_name='To distribute'),
        ),
        migrations.AddField(
            model_name='indexrange',
            name='indexer_cc_code',
            field=models.CharField(max_length=55, verbose_name='Indexer center code', blank=True),
        ),
        migrations.AddField(
            model_name='indexrange',
            name='selective',
            field=models.BooleanField(default=False, verbose_name='Selective'),
        ),
    ]
