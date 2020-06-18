# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0004_auto_20200618_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='updated_time',
            field=models.DateTimeField(auto_now=True, verbose_name='Last update', null=True),
        ),
    ]
