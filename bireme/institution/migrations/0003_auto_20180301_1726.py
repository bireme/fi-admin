# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0002_auto_20180223_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactperson',
            name='job_title',
            field=models.CharField(max_length=155, verbose_name='Job title', blank=True),
        ),
        migrations.AlterField(
            model_name='contactperson',
            name='name',
            field=models.CharField(max_length=155, verbose_name='Name', blank=True),
        ),
        migrations.AlterField(
            model_name='contactperson',
            name='prefix',
            field=models.CharField(blank=True, max_length=45, verbose_name='Prefix', choices=[(b'Mr.', 'Mr.'), (b'Mrs.', 'Mrs.'), (b'Dr.', 'Dr.')]),
        ),
        migrations.AlterField(
            model_name='institution',
            name='name',
            field=models.CharField(unique=True, max_length=254, verbose_name='Name', blank=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-2, 'Institution related'), (-1, 'Draft'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')]),
        ),
    ]
