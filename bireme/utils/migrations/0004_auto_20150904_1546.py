# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0003_auto_20150827_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auxcode',
            name='code',
            field=models.CharField(max_length=155, verbose_name='Code'),
            preserve_default=True,
        ),
    ]
