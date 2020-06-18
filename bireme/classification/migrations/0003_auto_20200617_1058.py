# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0002_collection_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='community',
            field=models.BooleanField(default=False, verbose_name='Community?'),
        ),
        migrations.AddField(
            model_name='collection',
            name='type',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='Collection type', choices=[(0, 'Category'), (1, 'Theme')]),
        ),
    ]
