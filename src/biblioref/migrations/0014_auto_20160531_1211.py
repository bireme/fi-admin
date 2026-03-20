# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0013_auto_20160502_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referencesource',
            name='title_collection',
            field=utils.fields.JSONField(null=True, verbose_name='Title', blank=True),
        ),
        migrations.AlterField(
            model_name='referencesource',
            name='title_monographic',
            field=utils.fields.JSONField(null=True, verbose_name='Title', blank=True),
        ),
    ]
