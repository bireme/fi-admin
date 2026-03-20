# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0002_auto_20161024_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acturl',
            name='url',
            field=models.URLField(max_length=300, verbose_name='URL'),
        ),
    ]
