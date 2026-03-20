# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0006_auto_20191021_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='country_area_code',
            field=models.CharField(max_length=20, verbose_name='Country/Area code', blank=True),
        ),
    ]
