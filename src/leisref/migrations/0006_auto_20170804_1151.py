# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leisref', '0005_act_reviewed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('scope_region', models.ForeignKey(verbose_name='Country/Region', blank=True, to='leisref.ActCountryRegion', null=True, on_delete=models.PROTECT)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Act collection',
                'verbose_name_plural': 'Act collections',
            },
        ),
        migrations.CreateModel(
            name='ActCollectionLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('act_collection', models.ForeignKey(to='leisref.ActCollection', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.AddField(
            model_name='act',
            name='act_collection',
            field=models.ForeignKey(verbose_name='Act collection', blank=True, to='leisref.ActCollection', null=True, on_delete=models.PROTECT),
        ),
    ]
