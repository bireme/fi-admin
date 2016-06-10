# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0015_auto_20160610_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referenceanalytic',
            name='title',
            field=utils.fields.JSONField(help_text='Field mandatory', null=True, verbose_name='Title', blank=True),
        ),
    ]
