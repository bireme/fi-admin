# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='oer',
            name='cooperative_center_code',
            field=models.CharField(max_length=55, verbose_name='Cooperative center', blank=True),
        ),
    ]
