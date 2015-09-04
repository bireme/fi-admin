# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0005_auto_20150904_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='check_tags',
            field=utils.fields.MultipleAuxiliaryChoiceField(max_length=100, verbose_name='Check tags', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reference',
            name='publication_type',
            field=utils.fields.MultipleAuxiliaryChoiceField(max_length=100, verbose_name='Publication type', blank=True),
            preserve_default=True,
        ),
    ]
