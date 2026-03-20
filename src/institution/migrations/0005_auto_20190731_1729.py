# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0004_auto_20190730_1515'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'verbose_name': 'Contact', 'verbose_name_plural': 'Contacts'},
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=155, verbose_name='Email', blank=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone_number',
            field=models.CharField(max_length=255, verbose_name='Phone', blank=True),
        ),
    ]
