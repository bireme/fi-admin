# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SuggestEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0, null=True, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Admitted'), (2, 'Refused'), (3, 'Deleted')])),
                ('title', models.CharField(max_length=455, verbose_name='Title')),
                ('start_date', models.DateField(help_text='day/month/year', verbose_name='Start date')),
                ('end_date', models.DateField(help_text='day/month/year', verbose_name='End date')),
                ('link', models.URLField(verbose_name='Link', blank=True)),
                ('city', models.CharField(max_length=125, verbose_name='City', blank=True)),
                ('administrative_comments', models.TextField(verbose_name='Administrative comments', blank=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
            ],
            options={
                'verbose_name': 'Suggested event',
                'verbose_name_plural': 'Suggested events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SuggestResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0, null=True, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Admitted'), (2, 'Refused'), (3, 'Deleted')])),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('link', models.URLField(verbose_name='Link')),
                ('abstract', models.TextField(verbose_name='abstract', blank=True)),
                ('keywords', models.TextField(verbose_name='Keywords', blank=True)),
                ('administrative_comments', models.TextField(verbose_name='Administrative comments', blank=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
            ],
            options={
                'verbose_name': 'Suggested resource',
                'verbose_name_plural': 'Suggested resources',
            },
            bases=(models.Model,),
        ),
    ]
