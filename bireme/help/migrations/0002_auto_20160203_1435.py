# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='help',
            name='help_text',
            field=tinymce.models.HTMLField(verbose_name='Help'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='helplocal',
            name='help_text',
            field=tinymce.models.HTMLField(verbose_name='Help'),
            preserve_default=True,
        ),
    ]
