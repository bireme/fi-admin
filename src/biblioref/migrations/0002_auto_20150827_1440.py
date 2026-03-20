# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0003_auto_20150827_1440'),
        ('biblioref', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='referencecomplement',
            name='conference_country',
            field=models.ForeignKey(verbose_name='Conference country', blank=True, to='utils.Country', null=True, on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='referencesource',
            name='publication_country',
            field=models.ForeignKey(verbose_name='Publication country', blank=True, to='utils.Country', null=True, on_delete=models.PROTECT),
            preserve_default=True,
        ),
    ]
