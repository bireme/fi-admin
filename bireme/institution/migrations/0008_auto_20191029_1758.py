# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0007_contact_country_area_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=55, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
            ],
            options={
                'verbose_name': 'Institution category',
                'verbose_name_plural': 'Institution categories',
            },
        ),
        migrations.CreateModel(
            name='CategoryLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=55, verbose_name='Name')),
                ('category', models.ForeignKey(verbose_name='Category', to='institution.Category')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.RemoveField(
            model_name='type',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='type',
            name='created_time',
        ),
        migrations.RemoveField(
            model_name='type',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='type',
            name='updated_time',
        ),
        migrations.AddField(
            model_name='adm',
            name='category_history',
            field=models.TextField(verbose_name='Category', blank=True),
        ),
        migrations.AddField(
            model_name='adm',
            name='type_history',
            field=models.TextField(verbose_name='Institution type', blank=True),
        ),
        migrations.RemoveField(
            model_name='adm',
            name='category',
        ),
        migrations.RemoveField(
            model_name='adm',
            name='type',
        ),
        migrations.AddField(
            model_name='adm',
            name='type',
            field=models.ManyToManyField(to='institution.Type', verbose_name='Type', blank=True),
        ),
        migrations.AlterField(
            model_name='type',
            name='name',
            field=models.CharField(max_length=55, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='typelocal',
            name='name',
            field=models.CharField(max_length=55, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='adm',
            name='category',
            field=models.ManyToManyField(to='institution.Category', verbose_name='Category', blank=True),
        ),
    ]
