# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0009_auto_20160203_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referenceanalytic',
            name='pages',
            field=utils.fields.JSONField(null=True, verbose_name='Pages', blank=True),
            preserve_default=True,
        ),
    ]
