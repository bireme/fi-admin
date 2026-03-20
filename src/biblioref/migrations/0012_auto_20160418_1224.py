# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0011_auto_20160415_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='publication_date',
            field=models.CharField(max_length=250, verbose_name='Publication date', blank=True),
        ),
        migrations.AlterField(
            model_name='referenceanalytic',
            name='clinical_trial_registry_name',
            field=utils.fields.JSONField(null=True, verbose_name='Clinical trial registry name', blank=True),
        ),
    ]
