# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0014_auto_20160531_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='referenceanalytic',
            name='thesis_dissertation_analytic_leader',
            field=utils.fields.JSONField(null=True, verbose_name='Leader', blank=True),
        ),
        migrations.AlterField(
            model_name='referencesource',
            name='thesis_dissertation_academic_title',
            field=models.CharField(max_length=250, verbose_name='Academic title', blank=True),
        ),
        migrations.AlterField(
            model_name='referencesource',
            name='thesis_dissertation_institution',
            field=models.CharField(max_length=300, verbose_name='Institution to which it is submitted', blank=True),
        ),
        migrations.AlterField(
            model_name='referencesource',
            name='thesis_dissertation_leader',
            field=utils.fields.JSONField(null=True, verbose_name='Leader', blank=True),
        ),
    ]
