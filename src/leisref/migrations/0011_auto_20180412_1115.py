# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0010_auto_20180124_1225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='act',
            name='act_collection',
        ),
        migrations.AddField(
            model_name='act',
            name='act_collection',
            field=models.ManyToManyField(to='leisref.ActCollection', verbose_name='Collection', blank=True),
        ),
    ]
