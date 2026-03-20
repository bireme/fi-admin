# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0004_auto_20150904_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='LA_Caribbean',
            field=models.BooleanField(default=False, verbose_name='Latin America & Caribbean region?'),
            preserve_default=True,
        ),
    ]
