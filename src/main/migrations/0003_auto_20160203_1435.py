# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150831_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='descriptor',
            name='text',
            field=models.CharField(max_length=255, verbose_name='Descriptor', blank=True),
            preserve_default=True,
        ),
    ]
