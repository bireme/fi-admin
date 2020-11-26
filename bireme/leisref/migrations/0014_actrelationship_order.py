# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0013_actalternateid'),
    ]

    operations = [
        migrations.AddField(
            model_name='actrelationship',
            name='order',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='order'),
        ),
    ]
