# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='act',
            name='effectiveness_date',
            field=models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Effectiveness date', blank=True),
        ),
        migrations.AlterField(
            model_name='act',
            name='issue_date',
            field=models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Issue date', blank=True),
        ),
        migrations.AlterField(
            model_name='act',
            name='publication_date',
            field=models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Publication date', blank=True),
        ),
        migrations.AlterField(
            model_name='act',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')]),
        ),
    ]
