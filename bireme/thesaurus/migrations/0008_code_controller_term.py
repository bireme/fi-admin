# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0007_auto_20181218_1031'),
    ]

    operations = [
        migrations.CreateModel(
            name='code_controller_term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequential_number', models.CharField(max_length=250, verbose_name='Sequential number')),
                ('thesaurus', models.CharField(max_length=50, verbose_name='Thesaurus', blank=True)),
            ],
            options={
                'verbose_name': 'Sequencial control',
                'verbose_name_plural': 'Sequencial controls',
            },
        ),
    ]
