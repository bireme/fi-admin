# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0023_auto_20170131_1147'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceDuplicate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('metadata_json', models.TextField(verbose_name='Metadata JSON', blank=True)),
                ('indexing_json', models.TextField(verbose_name='Indexing JSON', blank=True)),
                ('complement_json', models.TextField(verbose_name='Event/Project JSON', blank=True)),
                ('library_json', models.TextField(verbose_name='Library JSON', blank=True)),
                ('others_json', models.TextField(verbose_name='Other fields JSON', blank=True)),
                ('cooperative_center_code', models.CharField(max_length=55, verbose_name='Cooperative center', blank=True)),
                ('reference', models.ForeignKey(verbose_name='Reference', to='biblioref.Reference', on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Bibliographic Record Migration Duplicate',
                'verbose_name_plural': 'Bibliographic Migration Duplicates Records',
            },
        ),
    ]
