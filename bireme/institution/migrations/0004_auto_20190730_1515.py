# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tinymce.models
import log.models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0003_auto_20190607_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefix', models.CharField(blank=True, max_length=45, verbose_name='Prefix', choices=[(b'Mr.', 'Mr.'), (b'Mrs.', 'Mrs.'), (b'Dr.', 'Dr.')])),
                ('name', models.CharField(max_length=155, verbose_name='Name', blank=True)),
                ('job_title', models.CharField(max_length=155, verbose_name='Job title', blank=True)),
                ('email', models.EmailField(max_length=155, verbose_name='Email')),
                ('phone_number', models.CharField(max_length=255, verbose_name='Phone')),
                ('institution', models.ForeignKey(to='institution.Institution', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Contact person',
                'verbose_name_plural': 'Contact persons',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.AlterModelOptions(
            name='institutionadhesion',
            options={'verbose_name': 'Adhesion term', 'verbose_name_plural': 'Adhesion terms'},
        ),
        migrations.AlterField(
            model_name='adhesionterm',
            name='text',
            field=tinymce.models.HTMLField(verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='adhesiontermlocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='adhesiontermlocal',
            name='text',
            field=tinymce.models.HTMLField(verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='serviceproductlocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
    ]
