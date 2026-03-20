# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='descriptor',
            name='primary',
            field=models.BooleanField(default=False, verbose_name='Primary?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='keyword',
            name='user_recomendation',
            field=models.BooleanField(default=False, verbose_name='User recomendation?'),
            preserve_default=True,
        ),
    ]
