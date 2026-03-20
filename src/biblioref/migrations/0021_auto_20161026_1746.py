# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0020_reference_interoperability_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceAlternateID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alternate_id', models.CharField(max_length=55, verbose_name='Alternate id')),
            ],
            options={
                'verbose_name': 'Bibliographic Record Alternate ID',
                'verbose_name_plural': "Bibliographic Alternate ID's",
            },
        ),
        migrations.AlterField(
            model_name='reference',
            name='LILACS_original_id',
            field=models.CharField(verbose_name='LILACS id', max_length=8, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='reference',
            name='interoperability_source',
            field=models.CharField(verbose_name='Interoperability source', max_length=100, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='reference',
            name='software_version',
            field=models.CharField(verbose_name='Software version', max_length=50, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='referencealternateid',
            name='reference',
            field=models.ForeignKey(verbose_name='Reference', to='biblioref.Reference', on_delete=models.PROTECT),
        ),
    ]
