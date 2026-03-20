# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0008_auto_20150930_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='BIREME_reviewed',
            field=models.BooleanField(default=False, verbose_name='Reviewed by BIREME?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reference',
            name='publication_date_normalized',
            field=models.CharField(help_text='Format: YYYYMMDD', max_length=25, verbose_name='Publication normalized date', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reference',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (0, 'Inprocess'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')]),
            preserve_default=True,
        ),
    ]
