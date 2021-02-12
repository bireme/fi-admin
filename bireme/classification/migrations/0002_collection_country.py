# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0007_auto_20180220_1041'),
        ('classification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='country',
            field=models.ForeignKey(verbose_name='Country', blank=True, to='utils.Country', null=True, on_delete=models.PROTECT),
        ),
    ]
