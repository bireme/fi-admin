# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0012_auto_20160418_1224'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reference',
            options={'verbose_name': 'Bibliographic Record', 'verbose_name_plural': 'Bibliographic Records'},
        ),
        migrations.AlterModelOptions(
            name='referenceanalytic',
            options={'verbose_name': 'Bibliographic Record Analytic', 'verbose_name_plural': 'Bibliographic Records Analytic'},
        ),
        migrations.AlterModelOptions(
            name='referencecomplement',
            options={'verbose_name': 'Bibliographic Record Complement', 'verbose_name_plural': 'Bibliographic Records Complement'},
        ),
        migrations.AlterModelOptions(
            name='referencelocal',
            options={'verbose_name': 'Bibliographic Record Local', 'verbose_name_plural': 'Bibliographic Records Local'},
        ),
        migrations.AlterModelOptions(
            name='referencesource',
            options={'verbose_name': 'Bibliographic Record Source', 'verbose_name_plural': 'Bibliographic Records Source'},
        ),
        migrations.AddField(
            model_name='referencecomplement',
            name='project_number',
            field=models.CharField(max_length=155, verbose_name='Project number', blank=True),
        ),
    ]
