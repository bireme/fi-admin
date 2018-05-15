# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import log.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(related_name='relationship', to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=155, verbose_name='Name', blank=True)),
                ('slug', models.SlugField(max_length=155, verbose_name='Slug', blank=True)),
                ('parent', models.ForeignKey(verbose_name='Parent', blank=True, to='classification.Term', null=True)),
            ],
            options={
                'verbose_name': 'Term',
                'verbose_name_plural': 'Terms',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='TermLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=155, verbose_name='Name')),
                ('term', models.ForeignKey(verbose_name='Term', to='classification.Term')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=74, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Classification type',
                'verbose_name_plural': 'Classification types',
            },
        ),
        migrations.AddField(
            model_name='term',
            name='type',
            field=models.ForeignKey(verbose_name='Type', to='classification.Type'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='term',
            field=models.ForeignKey(verbose_name='Term', to='classification.Term'),
        ),
        migrations.AlterUniqueTogether(
            name='relationship',
            unique_together=set([('object_id', 'content_type', 'term')]),
        ),
    ]
