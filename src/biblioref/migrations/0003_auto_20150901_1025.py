# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0002_auto_20150827_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referenceanalytic',
            name='title',
            field=utils.fields.JSONField(null=True, verbose_name='Title'),
            preserve_default=True,
        ),
    ]
