# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20160316_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='not_regional_event',
            field=models.BooleanField(default=False, verbose_name='Do not publish in the regional event directory'),
        ),
    ]
