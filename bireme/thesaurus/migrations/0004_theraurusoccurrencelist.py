# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0003_auto_20181105_0926'),
    ]

    operations = [
        migrations.CreateModel(
            name='TheraurusOccurrenceList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('thesaurus_occurrence', models.CharField(max_length=250, verbose_name='Name of a thesaurus where terms occur', blank=True)),
                ('identifier_term', models.ForeignKey(related_name='tocurrence', blank=True, to='thesaurus.TermListDesc', null=True)),
            ],
            options={
                'verbose_name': 'Thesaurus occurrence',
                'verbose_name_plural': 'Thesaurus occurrence',
            },
        ),
    ]
