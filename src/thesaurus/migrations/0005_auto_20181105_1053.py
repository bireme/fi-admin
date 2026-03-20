# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0004_theraurusoccurrencelist'),
    ]

    operations = [
        migrations.CreateModel(
            name='TheraurusOccurrenceListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('thesaurus_occurrence', models.CharField(max_length=250, verbose_name='Name of a thesaurus where terms occur', blank=True)),
                ('identifier_term', models.ForeignKey(related_name='tocurrencedesc', blank=True, to='thesaurus.TermListDesc', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Thesaurus occurrence',
                'verbose_name_plural': 'Thesaurus occurrence',
            },
        ),
        migrations.RemoveField(
            model_name='theraurusoccurrencelist',
            name='identifier_term',
        ),
        migrations.DeleteModel(
            name='TheraurusOccurrenceList',
        ),
    ]
