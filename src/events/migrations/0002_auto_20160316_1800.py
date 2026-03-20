# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='contact_email',
            field=models.EmailField(max_length=254, verbose_name='Contact email', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='official_language',
            field=models.ManyToManyField(to='main.SourceLanguage', verbose_name='Official languages', blank=True),
        ),
    ]
