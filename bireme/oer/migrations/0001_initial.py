# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import log.models
import utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0004_auto_20170504_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='Audience',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Audience',
                'verbose_name_plural': 'Audiences',
            },
        ),
        migrations.CreateModel(
            name='AudienceLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('audience', models.ForeignKey(verbose_name='Audience', to='oer.Audience')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='CourseType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Course type',
                'verbose_name_plural': 'Course types',
            },
        ),
        migrations.CreateModel(
            name='CourseTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('coursetype', models.ForeignKey(verbose_name='Course type', to='oer.CourseType')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='Difficulty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Difficulty',
                'verbose_name_plural': 'Difficulties',
            },
        ),
        migrations.CreateModel(
            name='DifficultyLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('difficulty', models.ForeignKey(verbose_name='Difficulty', to='oer.Difficulty')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Format',
                'verbose_name_plural': 'Format',
            },
        ),
        migrations.CreateModel(
            name='FormatLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('format', models.ForeignKey(verbose_name='Format', to='oer.Format')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='InteractivityType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Interactivity type',
                'verbose_name_plural': 'Interactivity types',
            },
        ),
        migrations.CreateModel(
            name='InteractivityTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('interatype', models.ForeignKey(verbose_name='Interactivity type', to='oer.InteractivityType')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'License',
                'verbose_name_plural': 'Licenses',
            },
        ),
        migrations.CreateModel(
            name='LicenseLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('license', models.ForeignKey(verbose_name='License', to='oer.License')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='OER',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('status', models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-2, 'Related'), (-1, 'Draft'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')])),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('learning_objectives', models.TextField(verbose_name='Learning objectives', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('creator', utils.fields.JSONField(null=True, verbose_name='Creator', blank=True)),
                ('contributor', utils.fields.JSONField(null=True, verbose_name='Creator', blank=True)),
                ('aggregation_level', models.CharField(blank=True, max_length=55, verbose_name='Aggregation Level', choices=[(b'0', b'0'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4')])),
                ('publisher', models.CharField(max_length=155, verbose_name='Publisher', blank=True)),
                ('free_keywords', models.TextField(verbose_name='Free keywords', blank=True)),
                ('duration', models.CharField(max_length=155, verbose_name='Duration', blank=True)),
                ('size', models.CharField(max_length=55, verbose_name='Size', blank=True)),
                ('technical_requirements', models.CharField(max_length=155, verbose_name='Technical requirements', blank=True)),
                ('typical_learning_time', models.CharField(max_length=115, verbose_name='Typical learning time', blank=True)),
                ('audience', models.ManyToManyField(to='oer.Audience', verbose_name='Audience', blank=True)),
                ('course_type', models.ManyToManyField(to='oer.CourseType', verbose_name='Course type', blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('difficulty', models.ForeignKey(verbose_name='Difficulty', blank=True, to='oer.Difficulty', null=True)),
                ('format', models.ManyToManyField(to='oer.Format', verbose_name='Format', blank=True)),
                ('interactivity_type', models.ForeignKey(verbose_name='Interactivity type', blank=True, to='oer.InteractivityType', null=True)),
                ('language', models.ForeignKey(verbose_name='Language', blank=True, to='main.SourceLanguage', null=True)),
                ('license', models.ForeignKey(verbose_name='Rights license', blank=True, to='oer.License', null=True)),
            ],
            options={
                'verbose_name': 'OER reference',
                'verbose_name_plural': 'OER references',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='OERURL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('url', models.URLField(verbose_name='URL')),
                ('language', models.CharField(blank=True, max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('oer', models.ForeignKey(to='oer.OER', null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'URL',
                'verbose_name_plural': 'URLs',
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('oer_referred', models.ForeignKey(related_name='referred', verbose_name='OER related', to='oer.OER', null=True)),
                ('oer_related', models.ForeignKey(related_name='related', to='oer.OER', null=True)),
            ],
            options={
                'verbose_name': 'Relationship',
                'verbose_name_plural': 'Relationships',
            },
        ),
        migrations.CreateModel(
            name='RelationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=155, verbose_name='name')),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('label_present', models.CharField(max_length=155, verbose_name='Present tense form')),
                ('label_past', models.CharField(max_length=155, verbose_name='Past form')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Relation type',
                'verbose_name_plural': 'Relation types',
            },
        ),
        migrations.CreateModel(
            name='RelationTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('label_present', models.CharField(max_length=155, verbose_name='Present tense form')),
                ('label_past', models.CharField(max_length=155, verbose_name='Past form')),
                ('relation_type', models.ForeignKey(verbose_name='Relation type', to='oer.RelationType')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='TecResourceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Technical Resource Type',
                'verbose_name_plural': 'Technical Resource Types',
            },
        ),
        migrations.CreateModel(
            name='TecResourceTypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('tecresourcetype', models.ForeignKey(verbose_name='Technical resource type', to='oer.TecResourceType')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Type',
                'verbose_name_plural': 'Types',
            },
        ),
        migrations.CreateModel(
            name='TypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('oer_type', models.ForeignKey(verbose_name='Type', to='oer.Type')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.AddField(
            model_name='relationship',
            name='relation_type',
            field=models.ForeignKey(to='oer.RelationType'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='oer',
            name='tec_resource_type',
            field=models.ManyToManyField(to='oer.TecResourceType', verbose_name='Technical resource type', blank=True),
        ),
        migrations.AddField(
            model_name='oer',
            name='type',
            field=models.ForeignKey(verbose_name='Type', blank=True, to='oer.Type', null=True),
        ),
        migrations.AddField(
            model_name='oer',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
