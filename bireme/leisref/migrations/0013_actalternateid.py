# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0012_auto_20180823_1020'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActAlternateID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alternate_id', models.CharField(max_length=55, verbose_name='Alternate id')),
                ('act', models.ForeignKey(verbose_name='Act', to='leisref.Act')),
            ],
            options={
                'verbose_name': 'Act Alternate ID',
                'verbose_name_plural': "Act Alternate ID's",
            },
        ),
    ]
