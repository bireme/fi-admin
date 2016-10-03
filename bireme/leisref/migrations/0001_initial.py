# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import log.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0003_auto_20160203_1435'),
    ]

    operations = [
        migrations.CreateModel(
            name='Act',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('status', models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-2, 'Related'), (-1, 'Draft'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')])),
                ('act_number', models.CharField(max_length=125, verbose_name='Act number', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title', blank=True)),
                ('denomination', models.CharField(max_length=255, verbose_name='Denomination', blank=True)),
                ('scope_state', models.CharField(max_length=125, verbose_name='Act scope state', blank=True)),
                ('scope_city', models.CharField(max_length=125, verbose_name='Act scope city', blank=True)),
                ('scope_geo_group', models.CharField(max_length=125, verbose_name='Act scope geographic group', blank=True)),
                ('volumen', models.CharField(max_length=125, verbose_name='Volumen', blank=True)),
                ('fascicle_number', models.CharField(max_length=125, verbose_name='Fascicle', blank=True)),
                ('pages', models.CharField(max_length=125, verbose_name='Pages', blank=True)),
                ('issue_date', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Issue date', blank=True)),
                ('publication_date', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Publication date', blank=True)),
                ('effectiveness_date', models.DateField(help_text=b'DD/MM/YYYY', null=True, verbose_name='Effectiveness date', blank=True)),
                ('act_effectiveness', models.CharField(max_length=255, verbose_name='Act effectiveness', blank=True)),
                ('official_ementa', models.TextField(verbose_name='Official ementa', blank=True)),
                ('unofficial_ementa', models.TextField(verbose_name='Unofficial ementa', blank=True)),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
                ('institution_as_subject', models.TextField(verbose_name='Institution as subject', blank=True)),
                ('local_descriptors', models.TextField(verbose_name='Local descriptors', blank=True)),
                ('local_geo_descriptors', models.TextField(verbose_name='Local geographic descriptors', blank=True)),
            ],
            options={
                'verbose_name': 'Act reference',
                'verbose_name_plural': 'Act references',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='ActCountryRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Act country/region',
                'verbose_name_plural': 'Act country/region',
            },
        ),
        migrations.CreateModel(
            name='ActCountryRegionLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('act_region', models.ForeignKey(to='leisref.ActCountryRegion')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='ActOrganIssuer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('scope_region', models.ForeignKey(verbose_name='Country/Region', blank=True, to='leisref.ActCountryRegion', null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Organ issuer',
                'verbose_name_plural': 'Organ issuer',
            },
        ),
        migrations.CreateModel(
            name='ActOrganIssuerLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('organ_issuer', models.ForeignKey(verbose_name='Organ issuer', to='leisref.ActOrganIssuer')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='ActRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('act_apparatus', models.CharField(max_length=125, verbose_name='Apparatus', blank=True)),
                ('act_referred', models.ForeignKey(related_name='referred_set', verbose_name='Act related', to='leisref.Act')),
                ('act_related', models.ForeignKey(related_name='act_set', to='leisref.Act')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Act Relationship',
                'verbose_name_plural': 'Act Relationships',
            },
        ),
        migrations.CreateModel(
            name='ActRelationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=155, verbose_name='name')),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('label_present', models.CharField(max_length=155, verbose_name='Present tense form')),
                ('label_past', models.CharField(max_length=155, verbose_name='Past form')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('scope_region', models.ForeignKey(verbose_name='Country/Region', blank=True, to='leisref.ActCountryRegion', null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Act relation type',
                'verbose_name_plural': 'Act relation types',
            },
        ),
        migrations.CreateModel(
            name='ActRelationTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('relation_type', models.ForeignKey(verbose_name='Act relation type', to='leisref.ActRelationType')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='ActScope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('scope_region', models.ForeignKey(verbose_name='Country/Region', blank=True, to='leisref.ActCountryRegion', null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Act scope',
                'verbose_name_plural': 'Act scopes',
            },
        ),
        migrations.CreateModel(
            name='ActScopeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('act_scope', models.ForeignKey(to='leisref.ActScope')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='ActSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('scope_region', models.ForeignKey(verbose_name='Country/Region', blank=True, to='leisref.ActCountryRegion', null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Act source',
                'verbose_name_plural': 'Act sources',
            },
        ),
        migrations.CreateModel(
            name='ActSourceLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('act_source', models.ForeignKey(to='leisref.ActSource')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='ActType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('scope_region', models.ForeignKey(verbose_name='Country/Region', blank=True, to='leisref.ActCountryRegion', null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Act type',
                'verbose_name_plural': 'Act types',
            },
        ),
        migrations.CreateModel(
            name='ActTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('act_type', models.ForeignKey(verbose_name='Act type', to='leisref.ActType')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='ActURL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('url', models.URLField(verbose_name='URL')),
                ('language', models.CharField(blank=True, max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('act', models.ForeignKey(to='leisref.Act')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Act URL',
                'verbose_name_plural': 'Act URLs',
            },
        ),
        migrations.AddField(
            model_name='actrelationship',
            name='relation_type',
            field=models.ForeignKey(to='leisref.ActRelationType'),
        ),
        migrations.AddField(
            model_name='actrelationship',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='act',
            name='act_type',
            field=models.ForeignKey(verbose_name='Act type', to='leisref.ActType'),
        ),
        migrations.AddField(
            model_name='act',
            name='created_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='act',
            name='language',
            field=models.ForeignKey(verbose_name='Language', blank=True, to='main.SourceLanguage', null=True),
        ),
        migrations.AddField(
            model_name='act',
            name='organ_issuer',
            field=models.ForeignKey(verbose_name='Organ issuer', blank=True, to='leisref.ActOrganIssuer', null=True),
        ),
        migrations.AddField(
            model_name='act',
            name='scope',
            field=models.ForeignKey(verbose_name='Act scope', blank=True, to='leisref.ActScope', null=True),
        ),
        migrations.AddField(
            model_name='act',
            name='scope_region',
            field=models.ForeignKey(verbose_name='Act country/region', to='leisref.ActCountryRegion'),
        ),
        migrations.AddField(
            model_name='act',
            name='source_name',
            field=models.ForeignKey(verbose_name='Source name', blank=True, to='leisref.ActSource', null=True),
        ),
        migrations.AddField(
            model_name='act',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
