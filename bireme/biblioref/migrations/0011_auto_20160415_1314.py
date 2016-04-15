# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0010_auto_20160219_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='publication_date',
            field=models.CharField(max_length=250, verbose_name='Publication date'),
        ),
    ]
