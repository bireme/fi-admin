# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactphone',
            name='phone_number',
            field=models.CharField(max_length=255, verbose_name='Number'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')]),
        ),
    ]
