# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import log.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='code_controller',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequential_number', models.CharField(max_length=250, verbose_name='Sequential number')),
            ],
            options={
                'verbose_name': 'Sequencial control',
                'verbose_name_plural': 'Sequencial controls',
            },
        ),
        migrations.CreateModel(
            name='ConceptListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[(b'en', 'English'), (b'es', 'Spanish Latin America'), (b'pt-br', 'Portuguese'), (b'es-es', 'Spanish Spain'), (b'fr', 'French')])),
                ('scope_note', models.TextField(max_length=1500, verbose_name='Scope note', blank=True)),
            ],
            options={
                'verbose_name': 'Concept',
                'verbose_name_plural': 'Concepts',
            },
        ),
        migrations.CreateModel(
            name='ConceptListQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[(b'en', 'English'), (b'es', 'Spanish Latin America'), (b'pt-br', 'Portuguese'), (b'es-es', 'Spanish Spain'), (b'fr', 'French')])),
                ('scope_note', models.TextField(max_length=1500, verbose_name='Scope note', blank=True)),
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
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[(b'en', 'English'), (b'es', 'Spanish Latin America'), (b'pt-br', 'Portuguese'), (b'es-es', 'Spanish Spain'), (b'fr', 'French')])),
                ('annotation', models.TextField(max_length=1500, verbose_name='Annotation', blank=True)),
                ('history_note', models.TextField(max_length=1500, verbose_name='History note', blank=True)),
                ('online_note', models.TextField(max_length=1500, verbose_name='Online note', blank=True)),
                ('public_mesh_note', models.TextField(max_length=1500, verbose_name='Public MeSH note', blank=True)),
                ('consider_also', models.CharField(max_length=250, verbose_name='Consider also', blank=True)),
            ],
            options={
                'verbose_name': 'Description',
                'verbose_name_plural': 'Descriptions',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='DescriptionQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[(b'en', 'English'), (b'es', 'Spanish Latin America'), (b'pt-br', 'Portuguese'), (b'es-es', 'Spanish Spain'), (b'fr', 'French')])),
                ('annotation', models.TextField(max_length=1500, verbose_name='Annotation', blank=True)),
                ('history_note', models.TextField(max_length=1500, verbose_name='History note', blank=True)),
                ('online_note', models.TextField(max_length=1500, verbose_name='Online note', blank=True)),
            ],
            options={
                'verbose_name': 'Description of Qualifier',
                'verbose_name_plural': 'Descriptions of Qualifier',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='IdentifierConceptListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('concept_ui', models.CharField(max_length=50, verbose_name='Concept unique Identifier', blank=True)),
                ('concept_relation_name', models.CharField(blank=True, max_length=3, verbose_name='Relationship', choices=[(b'NRW', 'NRW - Narrower'), (b'BRD', 'BRD - Broader'), (b'REL', 'REL - Related but not broader or narrower')])),
                ('preferred_concept', models.CharField(blank=True, max_length=1, verbose_name='Preferred concept', choices=[(b'Y', 'Yes'), (b'N', 'No')])),
                ('casn1_name', models.TextField(max_length=1000, verbose_name='Chemical abstract', blank=True)),
                ('registry_number', models.CharField(max_length=250, verbose_name='Registry number from CAS', blank=True)),
            ],
            options={
                'verbose_name': 'Concept record',
                'verbose_name_plural': 'Concept records',
            },
        ),
        migrations.CreateModel(
            name='IdentifierConceptListQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('concept_ui', models.CharField(max_length=50, verbose_name='Concept unique Identifier', blank=True)),
                ('concept_relation_name', models.CharField(blank=True, max_length=3, verbose_name='Relationship', choices=[(b'NRW', 'NRW - Narrower'), (b'BRD', 'BRD - Broader'), (b'REL', 'REL - Related but not broader or narrower')])),
                ('preferred_concept', models.CharField(blank=True, max_length=1, verbose_name='Preferred concept', choices=[(b'Y', 'Yes'), (b'N', 'No')])),
                ('casn1_name', models.TextField(max_length=1000, verbose_name='Chemical abstract', blank=True)),
                ('registry_number', models.CharField(max_length=250, verbose_name='Registry number from CAS', blank=True)),
            ],
            options={
                'verbose_name': 'Concept record',
                'verbose_name_plural': 'Concept records',
            },
        ),
        migrations.CreateModel(
            name='IdentifierDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('descriptor_class', models.CharField(blank=True, max_length=2, verbose_name='Descriptor class', choices=[(b'1', '1 - Topical Descriptor'), (b'2', '2 - Publication Types, for example Review'), (b'3', '3 - Check Tag, e.g., Male - no tree number'), (b'4', '4 - Geographic Descriptor')])),
                ('descriptor_ui', models.CharField(max_length=250, verbose_name='MESH Descriptor UI', blank=True)),
                ('decs_code', models.CharField(max_length=250, verbose_name='DeCS Descriptor UI', blank=True)),
                ('external_code', models.CharField(max_length=250, verbose_name='External Descriptor UI', blank=True)),
                ('nlm_class_number', models.CharField(max_length=250, verbose_name='NLM classification number', blank=True)),
                ('date_created', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date created', blank=True)),
                ('date_revised', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date revised', blank=True)),
                ('date_established', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date established', blank=True)),
            ],
            options={
                'ordering': ('decs_code',),
                'verbose_name': 'Descriptor',
                'verbose_name_plural': 'Descriptors',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='IdentifierQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('qualifier_ui', models.CharField(max_length=250, verbose_name='MESH Qualifier UI', blank=True)),
                ('decs_code', models.CharField(max_length=250, verbose_name='DeCS Qualifier UI', blank=True)),
                ('external_code', models.CharField(max_length=250, verbose_name='External Qualifier UI', blank=True)),
                ('abbreviation', models.CharField(max_length=4, verbose_name='Abbreviation')),
                ('date_created', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date created', blank=True)),
                ('date_revised', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date revised', blank=True)),
                ('date_established', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date established', blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Qualifier',
                'verbose_name_plural': 'Qualifiers',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='legacyInformationDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pre_codificado', models.CharField(max_length=1, verbose_name='Pre-codificado', blank=True)),
                ('desastre', models.CharField(max_length=1, verbose_name='Desastre', blank=True)),
                ('reforma_saude', models.CharField(max_length=1, verbose_name='Reforma Saude', blank=True)),
                ('geografico', models.CharField(max_length=1, verbose_name='Geografico', blank=True)),
                ('mesh', models.CharField(max_length=1, verbose_name='MeSH', blank=True)),
                ('pt_lilacs', models.CharField(max_length=1, verbose_name='PT LILACS', blank=True)),
                ('nao_indexavel', models.CharField(max_length=1, verbose_name='Nao indexavel', blank=True)),
                ('homeopatia', models.CharField(max_length=1, verbose_name='Homeopatia', blank=True)),
                ('repidisca', models.CharField(max_length=1, verbose_name='Repidisca', blank=True)),
                ('saude_publica', models.CharField(max_length=1, verbose_name='Saude Publica', blank=True)),
                ('exploded', models.CharField(max_length=1, verbose_name='Exploded', blank=True)),
                ('geog_decs', models.CharField(max_length=1, verbose_name='Geog DeCS', blank=True)),
                ('identifier', models.ForeignKey(related_name='legacyinformationdesc', blank=True, to='thesaurus.IdentifierDesc', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Legacy information',
                'verbose_name_plural': 'Legacy information',
            },
        ),
        migrations.CreateModel(
            name='legacyInformationQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pre_codificado', models.CharField(max_length=1, verbose_name='Pre-codificado', blank=True)),
                ('desastre', models.CharField(max_length=1, verbose_name='Desastre', blank=True)),
                ('reforma_saude', models.CharField(max_length=1, verbose_name='Reforma Saude', blank=True)),
                ('geografico', models.CharField(max_length=1, verbose_name='Geografico', blank=True)),
                ('mesh', models.CharField(max_length=1, verbose_name='MeSH', blank=True)),
                ('pt_lilacs', models.CharField(max_length=1, verbose_name='PT LILACS', blank=True)),
                ('nao_indexavel', models.CharField(max_length=1, verbose_name='Nao indexavel', blank=True)),
                ('homeopatia', models.CharField(max_length=1, verbose_name='Homeopatia', blank=True)),
                ('repidisca', models.CharField(max_length=1, verbose_name='Repidisca', blank=True)),
                ('saude_publica', models.CharField(max_length=1, verbose_name='Saude Publica', blank=True)),
                ('exploded', models.CharField(max_length=1, verbose_name='Exploded', blank=True)),
                ('geog_decs', models.CharField(max_length=1, verbose_name='Geog DeCS', blank=True)),
                ('identifier', models.ForeignKey(related_name='legacyinformationqualif', blank=True, to='thesaurus.IdentifierQualif', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Legacy information',
                'verbose_name_plural': 'Legacy information',
            },
        ),
        migrations.CreateModel(
            name='PharmacologicalActionList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term_string', models.CharField(max_length=250, verbose_name='String', blank=True)),
                ('descriptor_ui', models.CharField(max_length=250, verbose_name='MESH Descriptor UI', blank=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[(b'en', 'English'), (b'es', 'Spanish Latin America'), (b'pt-br', 'Portuguese'), (b'es-es', 'Spanish Spain'), (b'fr', 'French')])),
                ('identifier', models.ForeignKey(related_name='pharmacodesc', blank=True, to='thesaurus.IdentifierDesc', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Pharmacological Action List',
                'verbose_name_plural': 'Pharmacologicals Action List',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='PreviousIndexingListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('previous_indexing', models.CharField(max_length=1000, verbose_name='Previous indexing', blank=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[(b'en', 'English'), (b'es', 'Spanish Latin America'), (b'pt-br', 'Portuguese'), (b'es-es', 'Spanish Spain'), (b'fr', 'French')])),
                ('identifier', models.ForeignKey(related_name='previousdesc', blank=True, to='thesaurus.IdentifierDesc', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Previous Indexing',
                'verbose_name_plural': 'Previous Indexing',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='SeeRelatedListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term_string', models.CharField(max_length=250, verbose_name='String', blank=True)),
                ('descriptor_ui', models.CharField(max_length=250, verbose_name='MESH Descriptor UI', blank=True)),
                ('identifier', models.ForeignKey(related_name='relateddesc', blank=True, to='thesaurus.IdentifierDesc', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'See Related List',
                'verbose_name_plural': 'See Related List',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='TermListDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (1, 'Published'), (5, 'Historical')])),
                ('term_ui', models.CharField(max_length=250, verbose_name='Term unique identifier', blank=True)),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[(b'en', 'English'), (b'es', 'Spanish Latin America'), (b'pt-br', 'Portuguese'), (b'es-es', 'Spanish Spain'), (b'fr', 'French')])),
                ('term_string', models.CharField(max_length=250, verbose_name='String')),
                ('concept_preferred_term', models.CharField(blank=True, max_length=1, verbose_name='Concept preferred term', choices=[(b'Y', 'Yes'), (b'N', 'No')])),
                ('is_permuted_term', models.CharField(blank=True, max_length=1, verbose_name='Is permuted term', choices=[(b'Y', 'Yes'), (b'N', 'No')])),
                ('lexical_tag', models.CharField(blank=True, max_length=3, verbose_name='Lexical categories', choices=[(b'ABB', 'ABB - Abbreviation'), (b'ABX', 'ABX - Embedded abbreviation'), (b'ACR', 'ACR - Acronym'), (b'ACX', 'ACX - Embedded acronym'), (b'EPO', 'EPO - Eponym'), (b'LAB', 'LAB - Lab number'), (b'NAM', 'NAM - Proper name'), (b'NON', 'NON - None'), (b'TRD', 'TRD - Trade name')])),
                ('record_preferred_term', models.CharField(blank=True, max_length=1, verbose_name='Record preferred term', choices=[(b'Y', 'Yes'), (b'N', 'No')])),
                ('entry_version', models.CharField(max_length=250, verbose_name='Entry version', blank=True)),
                ('date_created', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date created', blank=True)),
                ('date_altered', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date altered', blank=True)),
                ('historical_annotation', models.TextField(max_length=1500, verbose_name='Historical annotation', blank=True)),
                ('term_thesaurus', models.CharField(max_length=50, verbose_name='Thesaurus', blank=True)),
                ('identifier_concept', models.ForeignKey(related_name='termdesc', blank=True, to='thesaurus.IdentifierConceptListDesc', null=True, on_delete=models.PROTECT)),
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
                ('status', models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (1, 'Published'), (5, 'Historical')])),
                ('language_code', models.CharField(blank=True, max_length=10, verbose_name='Language used for description', choices=[(b'en', 'English'), (b'es', 'Spanish Latin America'), (b'pt-br', 'Portuguese'), (b'es-es', 'Spanish Spain'), (b'fr', 'French')])),
                ('concept_preferred_term', models.CharField(blank=True, max_length=1, verbose_name='Concept preferred term', choices=[(b'Y', 'Yes'), (b'N', 'No')])),
                ('is_permuted_term', models.CharField(blank=True, max_length=1, verbose_name='Is permuted term', choices=[(b'Y', 'Yes'), (b'N', 'No')])),
                ('lexical_tag', models.CharField(blank=True, max_length=3, verbose_name='Lexical categories', choices=[(b'ABB', 'ABB - Abbreviation'), (b'ABX', 'ABX - Embedded abbreviation'), (b'ACR', 'ACR - Acronym'), (b'ACX', 'ACX - Embedded acronym'), (b'EPO', 'EPO - Eponym'), (b'LAB', 'LAB - Lab number'), (b'NAM', 'NAM - Proper name'), (b'NON', 'NON - None'), (b'TRD', 'TRD - Trade name')])),
                ('record_preferred_term', models.CharField(blank=True, max_length=1, verbose_name='Record preferred term', choices=[(b'Y', 'Yes'), (b'N', 'No')])),
                ('term_ui', models.CharField(max_length=250, verbose_name='Term unique identifier', blank=True)),
                ('term_string', models.CharField(max_length=250, verbose_name='String', blank=True)),
                ('entry_version', models.CharField(max_length=250, verbose_name='Entry version', blank=True)),
                ('date_created', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date created', blank=True)),
                ('date_altered', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Date altered', blank=True)),
                ('historical_annotation', models.TextField(max_length=1500, verbose_name='Historical annotation', blank=True)),
                ('term_thesaurus', models.CharField(max_length=50, verbose_name='Thesaurus', blank=True)),
                ('identifier_concept', models.ForeignKey(related_name='termqualif', blank=True, to='thesaurus.IdentifierConceptListQualif', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'ordering': ('language_code', 'term_string', 'concept_preferred_term'),
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
                ('tree_number', models.CharField(max_length=250, verbose_name='Tree number', blank=True)),
                ('identifier', models.ForeignKey(related_name='dtreenumbers', to='thesaurus.IdentifierDesc', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'ordering': ('tree_number',),
                'verbose_name': 'Tree number for descriptor',
                'verbose_name_plural': 'Tree numbers for descriptors',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='TreeNumbersListQualif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tree_number', models.CharField(max_length=250, verbose_name='Tree number', blank=True)),
                ('identifier', models.ForeignKey(related_name='qtreenumbers', to='thesaurus.IdentifierQualif', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'ordering': ('tree_number',),
                'verbose_name': 'Tree number for qualifier',
                'verbose_name_plural': 'Tree numbers for qualifiers',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.AddField(
            model_name='identifierqualif',
            name='thesaurus',
            field=models.ForeignKey(default=None, to='thesaurus.Thesaurus', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='identifierqualif',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='identifierdesc',
            name='abbreviation',
            field=models.ManyToManyField(to='thesaurus.IdentifierQualif', verbose_name=b'Abbreviation', blank=True),
        ),
        migrations.AddField(
            model_name='identifierdesc',
            name='created_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='identifierdesc',
            name='thesaurus',
            field=models.ForeignKey(default=None, to='thesaurus.Thesaurus', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='identifierdesc',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='identifierconceptlistqualif',
            name='identifier',
            field=models.ForeignKey(blank=True, to='thesaurus.IdentifierQualif', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='identifierconceptlistdesc',
            name='identifier',
            field=models.ForeignKey(blank=True, to='thesaurus.IdentifierDesc', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='descriptionqualif',
            name='identifier',
            field=models.ForeignKey(related_name='descriptionqualif', to='thesaurus.IdentifierQualif', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='descriptiondesc',
            name='identifier',
            field=models.ForeignKey(related_name='descriptiondesc', to='thesaurus.IdentifierDesc', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='conceptlistqualif',
            name='identifier_concept',
            field=models.ForeignKey(related_name='conceptqualif', blank=True, to='thesaurus.IdentifierConceptListQualif', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='conceptlistdesc',
            name='identifier_concept',
            field=models.ForeignKey(related_name='conceptdesc', blank=True, to='thesaurus.IdentifierConceptListDesc', null=True, on_delete=models.PROTECT),
        ),
        migrations.AlterUniqueTogether(
            name='treenumberslistqualif',
            unique_together=set([('identifier', 'tree_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='treenumberslistdesc',
            unique_together=set([('identifier', 'tree_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='identifierqualif',
            unique_together=set([('thesaurus', 'abbreviation')]),
        ),
        migrations.AlterUniqueTogether(
            name='descriptionqualif',
            unique_together=set([('identifier', 'language_code')]),
        ),
        migrations.AlterUniqueTogether(
            name='descriptiondesc',
            unique_together=set([('identifier', 'language_code')]),
        ),
    ]
