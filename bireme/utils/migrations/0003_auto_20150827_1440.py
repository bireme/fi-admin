# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0002_auxcode_auxcodelocal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auxcode',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Label'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='auxcodelocal',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Label'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='auxcodelocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')]),
            preserve_default=True,
        ),
    ]
