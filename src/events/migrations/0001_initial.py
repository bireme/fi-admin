# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('status', models.SmallIntegerField(default=0, null=True, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Admitted'), (2, 'Refused'), (3, 'Deleted')])),
                ('title', models.CharField(max_length=455, verbose_name='Title')),
                ('start_date', models.DateField(help_text=b'DD/MM/YYYY', verbose_name='Start date')),
                ('end_date', models.DateField(help_text=b'DD/MM/YYYY', verbose_name='End date')),
                ('link', models.URLField(verbose_name='Link', blank=True)),
                ('address', models.CharField(max_length=255, verbose_name='Address', blank=True)),
                ('city', models.CharField(max_length=125, verbose_name='City', blank=True)),
                ('contact_email', models.EmailField(max_length=75, verbose_name='Contact email', blank=True)),
                ('contact_info', models.TextField(verbose_name='Information for contact', blank=True)),
                ('observations', models.TextField(verbose_name='Observations', blank=True)),
                ('target_groups', models.TextField(verbose_name='Target groups', blank=True)),
                ('cooperative_center_code', models.CharField(max_length=55, verbose_name='Cooperative center', blank=True)),
                ('country', models.ForeignKey(verbose_name='Country', blank=True, to='utils.Country', null=True, on_delete=models.PROTECT)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventType',
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
                'verbose_name': 'Event type',
                'verbose_name_plural': 'Event types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('event_type', models.ForeignKey(verbose_name='Event type', to='events.EventType', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ManyToManyField(to='events.EventType', verbose_name='Event type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='official_language',
            field=models.ManyToManyField(to='main.SourceLanguage', null=True, verbose_name='Official languages', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT),
            preserve_default=True,
        ),
    ]
