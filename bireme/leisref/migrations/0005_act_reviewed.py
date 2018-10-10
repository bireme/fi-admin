# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0004_auto_20170731_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='act',
            name='reviewed',
            field=models.BooleanField(default=False, verbose_name='Reviewed?'),
        ),
    ]
