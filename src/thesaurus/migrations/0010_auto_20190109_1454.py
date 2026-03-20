# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0009_auto_20190109_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identifierdesc',
            name='decs_code',
            field=models.CharField(max_length=250, verbose_name='Thesaurus UI', blank=True),
        ),
        migrations.AlterField(
            model_name='identifierdesc',
            name='descriptor_ui',
            field=models.CharField(max_length=250, verbose_name='Transport UI', blank=True),
        ),
        migrations.AlterField(
            model_name='identifierqualif',
            name='decs_code',
            field=models.CharField(max_length=250, verbose_name='Thesaurus UI', blank=True),
        ),
        migrations.AlterField(
            model_name='identifierqualif',
            name='qualifier_ui',
            field=models.CharField(max_length=250, verbose_name='Transport UI', blank=True),
        ),
        migrations.AlterField(
            model_name='pharmacologicalactionlist',
            name='descriptor_ui',
            field=models.CharField(max_length=250, verbose_name='Transport UI', blank=True),
        ),
        migrations.AlterField(
            model_name='seerelatedlistdesc',
            name='descriptor_ui',
            field=models.CharField(max_length=250, verbose_name='Transport UI', blank=True),
        ),
    ]
