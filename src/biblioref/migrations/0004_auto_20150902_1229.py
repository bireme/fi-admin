# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('biblioref', '0003_auto_20150901_1025'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('call_number', utils.fields.JSONField(null=True, verbose_name='Call number', blank=True)),
                ('database', models.TextField(verbose_name='Database', blank=True)),
                ('inventory_number', models.TextField(verbose_name='Inventory number', blank=True)),
                ('internal_note', models.TextField(verbose_name='Internal note', blank=True)),
                ('local_descriptors', models.TextField(verbose_name='Local descriptors', blank=True)),
                ('cooperative_center_code', models.CharField(max_length=55, verbose_name='Cooperative center', blank=True)),
                ('source', models.ForeignKey(verbose_name='Source', to='biblioref.Reference', on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Bibliographic Reference Local',
                'verbose_name_plural': 'Bibliographic References Local',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='referencecomplement',
            options={'verbose_name': 'Bibliographic Reference Complement', 'verbose_name_plural': 'Bibliographic References Complement'},
        ),
        migrations.AlterField(
            model_name='referenceanalytic',
            name='title',
            field=utils.fields.JSONField(help_text='Field mandatory', null=True, verbose_name='Title'),
            preserve_default=True,
        ),
    ]
