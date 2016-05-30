# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('title', '0003_auto_20160520_1709'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndexCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('code', models.CharField(max_length=55, verbose_name='Code', blank=True)),
                ('name', models.CharField(max_length=455, verbose_name='Name', blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Indexing Code',
                'verbose_name_plural': 'Indexing Codes',
            },
        ),
        migrations.AlterField(
            model_name='indexrange',
            name='index_code',
            field=models.ForeignKey(verbose_name='Index source code', blank=True, to='title.IndexCode', null=True),
        ),
        migrations.AlterField(
            model_name='titlevariance',
            name='initial_year',
            field=models.CharField(max_length=55, verbose_name='Initial year', blank=True),
        ),
    ]
