# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
        ('main', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('status', models.SmallIntegerField(default=0, null=True, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Admitted'), (2, 'Refused'), (3, 'Deleted')])),
                ('title', models.CharField(max_length=455, verbose_name='Original title')),
                ('title_translated', models.CharField(max_length=455, verbose_name='Translated title', blank=True)),
                ('link', models.URLField(verbose_name='Link')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('authors', models.TextField(help_text='Enter one per line', verbose_name='Authors', blank=True)),
                ('contributors', models.TextField(help_text='Enter one per line', verbose_name='Contributors', blank=True)),
                ('item_extension', models.CharField(max_length=255, verbose_name='Item extension', blank=True)),
                ('other_physical_details', models.CharField(max_length=255, verbose_name='Other physical details', blank=True)),
                ('dimension', models.CharField(max_length=255, verbose_name='Dimension', blank=True)),
                ('content_notes', models.TextField(verbose_name='Content notes', blank=True)),
                ('version_notes', models.TextField(verbose_name='Version notes', blank=True)),
                ('related_links', models.TextField(help_text='Enter one per line', verbose_name='Related links', blank=True)),
                ('publisher', models.CharField(max_length=255, verbose_name='Publisher', blank=True)),
                ('publication_date', models.DateField(help_text=b'Format: DD/MM/YYYY', null=True, verbose_name='Publication date', blank=True)),
                ('cooperative_center_code', models.CharField(max_length=55, verbose_name='Cooperative center', blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('language', models.ManyToManyField(to='main.SourceLanguage', verbose_name='language', blank=True)),
            ],
            options={
                'verbose_name': 'Media',
                'verbose_name_plural': 'Medias',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('date', models.DateField(help_text=b'Format: DD/MM/YYYY', null=True, verbose_name='Date', blank=True)),
                ('city', models.CharField(max_length=255, verbose_name='City', blank=True)),
                ('language', models.CharField(blank=True, max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('cooperative_center_code', models.CharField(max_length=55, verbose_name='Cooperative center', blank=True)),
                ('country', models.ForeignKey(verbose_name='Country', blank=True, to='utils.Country', null=True, on_delete=models.PROTECT)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Collection',
                'verbose_name_plural': 'Collections',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaCollectionLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('media_collection', models.ForeignKey(verbose_name='Collection', to='multimedia.MediaCollection', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('acronym', models.CharField(max_length=25, verbose_name='Acronym', blank=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Media type',
                'verbose_name_plural': 'Media types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('media_type', models.ForeignKey(verbose_name='Media type', to='multimedia.MediaType', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='media',
            name='media_collection',
            field=models.ForeignKey(verbose_name='Collection', blank=True, to='multimedia.MediaCollection', null=True, on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='media',
            name='media_type',
            field=models.ForeignKey(verbose_name='Media type', to='multimedia.MediaType', on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='media',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT),
            preserve_default=True,
        ),
    ]
