# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('status', models.SmallIntegerField(default=0, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Fixed'), (2, 'Invalid'), (3, 'SPAM')])),
                ('code', models.SmallIntegerField(default=3, verbose_name='Error type', choices=[(0, 'Invalid link'), (1, 'Bad content'), (2, 'Duplicated'), (3, 'Other')])),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('new_link', models.URLField(verbose_name='New link', blank=True)),
                ('content_type', models.ForeignKey(related_name='error_reporting', to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Error report',
                'verbose_name_plural': 'Error reports',
            },
            bases=(models.Model,),
        ),
    ]
