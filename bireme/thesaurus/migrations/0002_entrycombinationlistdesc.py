# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import log.models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryCombinationListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ecin_qualif', models.CharField(max_length=250, verbose_name='Qualifier string', blank=True)),
                ('ecin_id', models.CharField(max_length=250, verbose_name='Identifier', blank=True)),
                ('ecout_desc', models.CharField(max_length=250, verbose_name='Descriptor string', blank=True)),
                ('ecout_id', models.CharField(max_length=250, verbose_name='Identifier', blank=True)),
                ('identifier', models.ForeignKey(related_name='entrycombinationlistdesc', blank=True, to='thesaurus.IdentifierDesc', null=True)),
            ],
            options={
                'verbose_name': 'Entry combination List',
                'verbose_name_plural': 'Entry combinations List',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
    ]
