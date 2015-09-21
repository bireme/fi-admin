# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0006_auto_20150904_1533'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reference',
            name='call_number',
        ),
        migrations.RemoveField(
            model_name='reference',
            name='database',
        ),
        migrations.RemoveField(
            model_name='referencesource',
            name='inventory_number',
        ),
    ]
