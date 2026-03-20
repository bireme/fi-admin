# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Help',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=25, verbose_name='Source', choices=[(b'resources', 'Resources'), (b'events', 'Events'), (b'biblioref', 'Bibliographic Reference')])),
                ('field', models.CharField(max_length=55, verbose_name='Field name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('help_text', models.TextField(verbose_name='Help')),
            ],
            options={
                'verbose_name': 'Help',
                'verbose_name_plural': 'Helps',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HelpLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('help_text', models.TextField(verbose_name='Help')),
                ('help', models.ForeignKey(verbose_name='Help', to='help.Help', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
            bases=(models.Model,),
        ),
    ]
