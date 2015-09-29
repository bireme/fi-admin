# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fascic',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='fascic',
            name='mask',
        ),
        migrations.RemoveField(
            model_name='fascic',
            name='title',
        ),
        migrations.RemoveField(
            model_name='fascic',
            name='updated_by',
        ),
        migrations.DeleteModel(
            name='Fascic',
        ),
        migrations.RemoveField(
            model_name='mask',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='mask',
            name='updated_by',
        ),
        migrations.DeleteModel(
            name='Mask',
        ),
        migrations.AlterField(
            model_name='onlineresources',
            name='url',
            field=models.URLField(max_length=255, verbose_name='URL', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='title',
            name='issn',
            field=models.CharField(max_length=255, verbose_name='ISSN', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='title',
            name='national_code',
            field=models.CharField(max_length=55, verbose_name='National code', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='title',
            name='related_systems',
            field=models.TextField(help_text='Enter one per line', verbose_name='Related systems', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='title',
            name='secs_number',
            field=models.CharField(max_length=55, verbose_name='SeCS number', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='title',
            name='section',
            field=models.CharField(max_length=255, verbose_name='Section/Part', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='title',
            name='section_title',
            field=models.CharField(max_length=455, verbose_name='Section/Part title', blank=True),
            preserve_default=True,
        ),
    ]
