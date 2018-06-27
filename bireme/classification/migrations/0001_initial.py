# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import log.models
import classification.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=155, verbose_name='Name', blank=True)),
                ('slug', models.SlugField(max_length=155, verbose_name='Slug', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('image', models.FileField(upload_to=classification.models.attachment_upload, verbose_name='Image', blank=True)),
                ('parent', models.ForeignKey(verbose_name='Parent', blank=True, to='classification.Collection', null=True)),
            ],
            options={
                'verbose_name': 'Collection',
                'verbose_name_plural': 'Collections',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='CollectionLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=155, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('image', models.FileField(upload_to=classification.models.attachment_upload, verbose_name='Image', blank=True)),
                ('collection', models.ForeignKey(verbose_name='Collection', to='classification.Collection')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('collection', models.ForeignKey(verbose_name='Collection', to='classification.Collection')),
                ('content_type', models.ForeignKey(related_name='relationship', to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='relationship',
            unique_together=set([('object_id', 'content_type', 'collection')]),
        ),
    ]
