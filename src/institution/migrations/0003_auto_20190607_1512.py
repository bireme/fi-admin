# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import log.models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0002_auto_20190604_1119'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdhesionTerm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='Text')),
                ('version', models.CharField(max_length=25, verbose_name='Version', blank=True)),
            ],
            options={
                'verbose_name': 'Adhesion term',
                'verbose_name_plural': 'Adhesion terms',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='AdhesionTermLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('text', models.TextField(verbose_name='Text')),
                ('adhesionterm', models.ForeignKey(verbose_name='Adhesion term', to='institution.AdhesionTerm', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='InstitutionAdhesion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('acepted', models.BooleanField(default=False, verbose_name='Acepted')),
                ('adhesionterm', models.ForeignKey(to='institution.AdhesionTerm', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Adhesion term level',
                'verbose_name_plural': 'Adhesion terms',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='InstitutionServiceProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Institution service product',
                'verbose_name_plural': 'Instituion services products',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='ServiceProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=155, verbose_name='Name', blank=True)),
                ('acronym', models.CharField(max_length=35, verbose_name='Acronym', blank=True)),
            ],
            options={
                'verbose_name': 'Service/Product',
                'verbose_name_plural': 'Services/Products',
            },
        ),
        migrations.CreateModel(
            name='ServiceProductLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=155, verbose_name='Name', blank=True)),
                ('serviceproduct', models.ForeignKey(verbose_name='Service/Product', to='institution.ServiceProduct', on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.AlterField(
            model_name='institution',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (1, 'Active'), (2, 'Inactive'), (3, 'Deleted')]),
        ),
        migrations.AddField(
            model_name='institutionserviceproduct',
            name='institution',
            field=models.ForeignKey(to='institution.Institution', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='institutionserviceproduct',
            name='serviceproduct',
            field=models.ForeignKey(to='institution.ServiceProduct', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='institutionadhesion',
            name='institution',
            field=models.ForeignKey(to='institution.Institution', null=True, on_delete=models.PROTECT),
        ),
    ]
