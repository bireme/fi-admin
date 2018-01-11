# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConceptListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[('eng', 'English'), ('spa_la', 'Spanish Latin America'), ('por', 'Portuguese'), ('spa_es', 'Spanish Spain'), ('fre', 'French')])),
                ('preferred_concept', models.CharField(blank=True, max_length=1, verbose_name='Preferred concept', choices=[('Y', 'Yes'), ('N', 'No')])),
                ('concept_ui', models.CharField(max_length=50, null=True, verbose_name='Concept unique Identifier', blank=True)),
                ('concept_name', models.CharField(max_length=250, null=True, verbose_name='Concept name', blank=True)),
                ('casn1_name', models.TextField(max_length=1000, null=True, verbose_name='Chemical abstract', blank=True)),
                ('registry_number', models.CharField(max_length=250, null=True, verbose_name='Registry number from CAS', blank=True)),
                ('relation_name', models.CharField(blank=True, max_length=3, verbose_name='Concept relation', choices=[('BRD', 'BRD - Broader'), ('NRW', 'NRW - Narrower'), ('REL', 'REL - Related but not broader or narrower')])),
                ('concept1_ui', models.CharField(max_length=250, null=True, verbose_name='First concept in then Concept relation', blank=True)),
                ('concept2_ui', models.CharField(max_length=250, null=True, verbose_name='Second concept in then Concept relation', blank=True)),
            ],
            options={
                'verbose_name': 'Concept',
                'verbose_name_plural': 'Concepts',
            },
        ),
        migrations.CreateModel(
            name='DescriptionDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[('eng', 'English'), ('spa_la', 'Spanish Latin America'), ('por', 'Portuguese'), ('spa_es', 'Spanish Spain'), ('fre', 'French')])),
                ('descriptor_name', models.CharField(max_length=250, verbose_name='Term name')),
                ('annotation', models.TextField(max_length=1500, null=True, verbose_name='Annotation', blank=True)),
                ('history_note', models.TextField(max_length=1500, null=True, verbose_name='History note', blank=True)),
                ('online_note', models.TextField(max_length=1500, null=True, verbose_name='Online note', blank=True)),
                ('scope_note', models.TextField(max_length=1500, null=True, verbose_name='Scope note', blank=True)),
                ('public_mesh_note', models.TextField(max_length=1500, null=True, verbose_name='Public MeSH note', blank=True)),
                ('consider_also', models.CharField(max_length=250, null=True, verbose_name='Consider also', blank=True)),
            ],
            options={
                'verbose_name': 'Description',
                'verbose_name_plural': 'Descriptions',
            },
        ),
        migrations.CreateModel(
            name='DescriptionQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[('eng', 'English'), ('spa_la', 'Spanish Latin America'), ('por', 'Portuguese'), ('spa_es', 'Spanish Spain'), ('fre', 'French')])),
                ('qualifier_name', models.CharField(max_length=250, verbose_name='Qualifier name')),
                ('annotation', models.TextField(max_length=1500, null=True, verbose_name='Annotation', blank=True)),
                ('history_note', models.TextField(max_length=1500, null=True, verbose_name='History note', blank=True)),
                ('online_note', models.TextField(max_length=1500, null=True, verbose_name='Online note', blank=True)),
                ('scope_note', models.TextField(max_length=1500, null=True, verbose_name='Scope note', blank=True)),
            ],
            options={
                'verbose_name': 'Description of Qualifier',
                'verbose_name_plural': 'Descriptions of Qualifier',
            },
        ),
        migrations.CreateModel(
            name='IdentifierDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True, help_text='Check to set it to active', verbose_name='Enabled')),
                ('descriptor_class', models.CharField(blank=True, max_length=2, verbose_name='Descriptor class', choices=[('1', '1 - Topical Descriptor'), ('2', '2 - Publication Types, for example Review'), ('3', '3 - Check Tag, e.g., Male - no tree number'), ('4', '4 - Geographic Descriptor')])),
                ('descriptor_ui', models.CharField(max_length=250, null=True, verbose_name='MESH Descriptor UI', blank=True)),
                ('decs_code', models.CharField(max_length=250, null=True, verbose_name='DeCS Descriptor UI', blank=True)),
                ('external_code', models.CharField(max_length=250, null=True, verbose_name='External Descriptor UI', blank=True)),
                ('nlm_class_number', models.CharField(max_length=250, null=True, verbose_name='NLM classification number', blank=True)),
                ('date_created', models.DateField(null=True, verbose_name='Date created', blank=True)),
                ('date_revised', models.DateField(null=True, verbose_name='Date revised', blank=True)),
                ('date_established', models.DateField(null=True, verbose_name='Date established', blank=True)),
            ],
            options={
                'ordering': ('decs_code',),
                'verbose_name': 'Descriptor',
                'verbose_name_plural': 'Descriptors',
            },
        ),
        migrations.CreateModel(
            name='IdentifierQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True, help_text='Check to set it to active', verbose_name='Enabled')),
                ('qualifier_ui', models.CharField(max_length=250, null=True, verbose_name='MESH Qualifier UI', blank=True)),
                ('decs_code', models.CharField(max_length=250, null=True, verbose_name='DeCS Qualifier UI', blank=True)),
                ('external_code', models.CharField(max_length=250, null=True, verbose_name='External Qualifier UI', blank=True)),
                ('abbreviation', models.CharField(max_length=4, null=True, verbose_name='Abbreviation', blank=True)),
                ('date_created', models.DateField(null=True, verbose_name='Date created', blank=True)),
                ('date_revised', models.DateField(null=True, verbose_name='Date revised', blank=True)),
                ('date_established', models.DateField(null=True, verbose_name='Date established', blank=True)),
            ],
            options={
                'ordering': ('abbreviation',),
                'verbose_name': 'Qualifier',
                'verbose_name_plural': 'Qualifiers',
            },
        ),
        migrations.CreateModel(
            name='PreviousIndexingListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('previous_indexing', models.CharField(max_length=250, null=True, verbose_name='Previous indexing', blank=True)),
                ('identifier', models.ForeignKey(to='thesaurus.IdentifierDesc')),
            ],
            options={
                'verbose_name': 'Previous Indexing',
                'verbose_name_plural': 'Previous Indexing',
            },
        ),
        migrations.CreateModel(
            name='TermListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[('eng', 'English'), ('spa_la', 'Spanish Latin America'), ('por', 'Portuguese'), ('spa_es', 'Spanish Spain'), ('fre', 'French')])),
                ('concept_preferred_term', models.CharField(blank=True, max_length=1, verbose_name='Concept preferred term', choices=[('Y', 'Yes'), ('N', 'No')])),
                ('is_permuted_term', models.CharField(blank=True, max_length=1, verbose_name='Is permuted term', choices=[('Y', 'Yes'), ('N', 'No')])),
                ('lexical_tag', models.CharField(blank=True, max_length=3, verbose_name='Lexical categories', choices=[('ABB', 'ABB - Abbreviation'), ('ABX', 'ABX - Embedded abbreviation'), ('ACR', 'ACR - Acronym'), ('ACX', 'ACX - Embedded acronym'), ('EPO', 'EPO - Eponym'), ('LAB', 'LAB - Lab number'), ('NAM', 'NAM - Proper name'), ('NON', 'NON - None'), ('TRD', 'TRD - Trade name')])),
                ('record_preferred_term', models.CharField(blank=True, max_length=1, verbose_name='Record preferred term', choices=[('Y', 'Yes'), ('N', 'No')])),
                ('term_ui', models.CharField(max_length=250, null=True, verbose_name='Term unique identifier', blank=True)),
                ('term_string', models.CharField(max_length=250, verbose_name='String')),
                ('entry_version', models.CharField(max_length=250, verbose_name='Entry version', blank=True)),
                ('date_created', models.DateField(null=True, verbose_name='Date created', blank=True)),
                ('identifier', models.ForeignKey(to='thesaurus.IdentifierDesc')),
            ],
            options={
                'verbose_name': 'Term',
                'verbose_name_plural': 'Terms',
            },
        ),
        migrations.CreateModel(
            name='TermListQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[('eng', 'English'), ('spa_la', 'Spanish Latin America'), ('por', 'Portuguese'), ('spa_es', 'Spanish Spain'), ('fre', 'French')])),
                ('concept_preferred_term', models.CharField(blank=True, max_length=1, verbose_name='Concept preferred term', choices=[('Y', 'Yes'), ('N', 'No')])),
                ('is_permuted_term', models.CharField(blank=True, max_length=1, verbose_name='Is permuted term', choices=[('Y', 'Yes'), ('N', 'No')])),
                ('lexical_tag', models.CharField(blank=True, max_length=3, verbose_name='Lexical categories', choices=[('ABB', 'ABB - Abbreviation'), ('ABX', 'ABX - Embedded abbreviation'), ('ACR', 'ACR - Acronym'), ('ACX', 'ACX - Embedded acronym'), ('EPO', 'EPO - Eponym'), ('LAB', 'LAB - Lab number'), ('NAM', 'NAM - Proper name'), ('NON', 'NON - None'), ('TRD', 'TRD - Trade name')])),
                ('record_preferred_term', models.CharField(blank=True, max_length=1, verbose_name='Record preferred term', choices=[('Y', 'Yes'), ('N', 'No')])),
                ('term_ui', models.CharField(max_length=250, null=True, verbose_name='Term unique identifier', blank=True)),
                ('term_string', models.CharField(max_length=250, verbose_name='String')),
                ('entry_version', models.CharField(max_length=250, verbose_name='Entry version', blank=True)),
                ('date_created', models.DateField(null=True, verbose_name='Date created', blank=True)),
                ('identifier', models.ForeignKey(to='thesaurus.IdentifierQualif')),
            ],
            options={
                'verbose_name': 'Term',
                'verbose_name_plural': 'Terms',
            },
        ),
        migrations.CreateModel(
            name='Thesaurus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('thesaurus_name', models.CharField(max_length=250, verbose_name='Thesaurus name')),
                ('thesaurus_author', models.CharField(max_length=250, verbose_name='Author')),
                ('thesaurus_scope', models.CharField(max_length=250, verbose_name='Scope')),
            ],
            options={
                'verbose_name': 'Thesaurus',
                'verbose_name_plural': 'Thesaurus',
            },
        ),
        migrations.CreateModel(
            name='TreeNumbersListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tree_number', models.CharField(max_length=250, null=True, verbose_name='Tree number', blank=True)),
                ('identifier', models.ForeignKey(to='thesaurus.IdentifierDesc')),
            ],
            options={
                'verbose_name': 'Tree number for descriptor',
                'verbose_name_plural': 'Tree numbers for descriptors',
            },
        ),
        migrations.CreateModel(
            name='TreeNumbersListQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tree_number', models.CharField(max_length=250, null=True, verbose_name='Tree number', blank=True)),
                ('identifier', models.ForeignKey(to='thesaurus.IdentifierQualif')),
            ],
            options={
                'verbose_name': 'Tree number for qualifier',
                'verbose_name_plural': 'Tree numbers for qualifiers',
            },
        ),
        migrations.AddField(
            model_name='identifierqualif',
            name='thesaurus',
            field=models.ForeignKey(default=None, blank=True, to='thesaurus.Thesaurus', null=True),
        ),
        migrations.AddField(
            model_name='identifierdesc',
            name='abbreviation',
            field=models.ManyToManyField(to='thesaurus.IdentifierQualif', verbose_name='Abbreviation'),
        ),
        migrations.AddField(
            model_name='identifierdesc',
            name='thesaurus',
            field=models.ForeignKey(default=None, blank=True, to='thesaurus.Thesaurus', null=True),
        ),
        migrations.AddField(
            model_name='descriptionqualif',
            name='identifier',
            field=models.ForeignKey(to='thesaurus.IdentifierQualif'),
        ),
        migrations.AddField(
            model_name='descriptiondesc',
            name='identifier',
            field=models.ForeignKey(to='thesaurus.IdentifierDesc'),
        ),
        migrations.AddField(
            model_name='conceptlistdesc',
            name='identifier',
            field=models.ForeignKey(to='thesaurus.IdentifierDesc'),
        ),
    ]
