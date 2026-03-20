# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Descriptor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('text', models.CharField(max_length=255, verbose_name='Text', blank=True)),
                ('code', models.CharField(max_length=50, verbose_name='Code', blank=True)),
                ('status', models.SmallIntegerField(default=0, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Admitted'), (2, 'Refused')])),
                ('content_type', models.ForeignKey(related_name='descriptors', to='contenttypes.ContentType', on_delete=models.PROTECT),),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('text', models.CharField(max_length=255, verbose_name='Text', blank=True)),
                ('status', models.SmallIntegerField(default=0, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Admitted'), (2, 'Refused')])),
                ('user_recomendation', models.BooleanField(verbose_name='User recomendation?')),
                ('content_type', models.ForeignKey(related_name='keywords', to='contenttypes.ContentType', on_delete=models.PROTECT)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('status', models.SmallIntegerField(default=0, null=True, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Admitted'), (2, 'Refused'), (3, 'Deleted')])),
                ('title', models.CharField(max_length=510, verbose_name='Title')),
                ('link', models.TextField(verbose_name='Link')),
                ('originator', models.TextField(verbose_name='Originator')),
                ('author', models.TextField(help_text='Enter one per line', verbose_name='Authors', blank=True)),
                ('abstract', models.TextField(verbose_name='Abstract')),
                ('time_period_textual', models.CharField(max_length=255, verbose_name='Temporal range', blank=True)),
                ('objective', models.TextField(verbose_name='Objective', blank=True)),
                ('cooperative_center_code', models.CharField(max_length=55, verbose_name='Cooperative center', blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('originator_location', models.ManyToManyField(to='utils.Country', verbose_name='Originator location')),
            ],
            options={
                'verbose_name': 'Resource',
                'verbose_name_plural': 'Resources',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceThematic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('status', models.SmallIntegerField(default=0, blank=True, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Admitted'), (2, 'Refused')])),
                ('content_type', models.ForeignKey(related_name='thematics', to='contenttypes.ContentType', on_delete=models.PROTECT)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Thematic area',
                'verbose_name_plural': 'Thematic areas',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SourceLanguage',
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
                'verbose_name': 'Source language',
                'verbose_name_plural': 'Source languages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SourceLanguageLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('source_language', models.ForeignKey(verbose_name='Source language', to='main.SourceLanguage', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SourceType',
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
                'verbose_name': 'source type',
                'verbose_name_plural': 'source types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SourceTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('source_type', models.ForeignKey(verbose_name='Source type', to='main.SourceType', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ThematicArea',
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
                'verbose_name': 'Thematic area',
                'verbose_name_plural': 'Thematic areas',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ThematicAreaLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('thematic_area', models.ForeignKey(verbose_name='Thematic area', to='main.ThematicArea', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='resourcethematic',
            name='thematic_area',
            field=models.ForeignKey(related_name='+', to='main.ThematicArea', on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcethematic',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='source_language',
            field=models.ManyToManyField(to='main.SourceLanguage', verbose_name='Source language'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='source_type',
            field=models.ManyToManyField(to='main.SourceType', verbose_name='Source type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT),
            preserve_default=True,
        ),
    ]
