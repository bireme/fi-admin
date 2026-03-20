# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0024_referenceduplicate'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='referenceduplicate',
            options={'verbose_name': 'Duplicate Bibliographic Record', 'verbose_name_plural': 'Duplicate Bibliographic Records'},
        ),
        migrations.AlterField(
            model_name='reference',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-3, 'Migration'), (-2, 'Submission'), (-1, 'Draft'), (0, 'Inprocess'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')]),
        ),
        migrations.AlterField(
            model_name='referencesource',
            name='english_title_monographic',
            field=models.CharField(max_length=400, verbose_name='English translated title', blank=True),
        ),
    ]
