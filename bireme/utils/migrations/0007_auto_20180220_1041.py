# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0006_auto_20170621_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auxcode',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='auxcodelocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='countrylocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
    ]
