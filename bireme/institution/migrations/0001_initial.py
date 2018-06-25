# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import log.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('utils', '0007_auto_20180220_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.TextField(verbose_name='Category', blank=True)),
                ('type', models.TextField(verbose_name='Institution type', blank=True)),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
            ],
            options={
                'verbose_name': 'Administrative information',
                'verbose_name_plural': 'Administrative informations',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='ContactEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_type', models.CharField(max_length=75, verbose_name='Type', choices=[(b'main', 'Main'), (b'other', 'Other')])),
                ('email_name', models.CharField(max_length=85, verbose_name='Name')),
                ('email', models.EmailField(max_length=155, verbose_name='Email')),
            ],
            options={
                'verbose_name': 'Contact email',
                'verbose_name_plural': 'Contact emails',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='ContactPerson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefix', models.CharField(blank=True, max_length=45, verbose_name='Prefix', choices=[(b'Mr.', 'Mr.'), (b'Mrs.', 'Mrs.'), (b'Dr.', 'Dr.')])),
                ('name', models.CharField(max_length=155, verbose_name='Name', blank=True)),
                ('job_title', models.CharField(max_length=155, verbose_name='Job title', blank=True)),
            ],
            options={
                'verbose_name': 'Contact person',
                'verbose_name_plural': 'Contact persons',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='ContactPhone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_type', models.CharField(max_length=75, verbose_name='Type', choices=[(b'main', 'Main'), (b'extension', 'Extension'), (b'fax', 'Fax')])),
                ('phone_name', models.CharField(max_length=85, verbose_name='Name')),
                ('country_code', models.CharField(max_length=4, verbose_name='Country code')),
                ('phone_number', models.CharField(max_length=55, verbose_name='Number')),
            ],
            options={
                'verbose_name': 'Contact phone',
                'verbose_name_plural': 'Contact phones',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('status', models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-2, 'Institution related'), (-1, 'Draft'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')])),
                ('cc_code', models.CharField(unique=True, max_length=55, verbose_name='Center code')),
                ('name', models.CharField(max_length=254, verbose_name='Name', blank=True)),
                ('acronym', models.CharField(max_length=55, verbose_name='Acronym', blank=True)),
                ('address', models.CharField(max_length=255, verbose_name='Address', blank=True)),
                ('city', models.CharField(max_length=155, verbose_name='City', blank=True)),
                ('state', models.CharField(max_length=155, verbose_name='State', blank=True)),
                ('zipcode', models.CharField(max_length=75, verbose_name='Zip code', blank=True)),
                ('mailbox', models.CharField(max_length=75, verbose_name='Mailbox', blank=True)),
                ('cooperative_center_code', models.CharField(max_length=55, verbose_name='Cooperative center', blank=True)),
                ('country', models.ForeignKey(verbose_name='Country', blank=True, to='utils.Country', null=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Institution',
                'verbose_name_plural': 'Institutions',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=155, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Institution type',
                'verbose_name_plural': 'Institution types',
            },
        ),
        migrations.CreateModel(
            name='TypeLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=155, verbose_name='Name')),
                ('type', models.ForeignKey(verbose_name='Type', to='institution.Type')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=254, verbose_name='Name', blank=True)),
                ('acronym', models.CharField(max_length=55, verbose_name='Acronym', blank=True)),
                ('country', models.ForeignKey(verbose_name='Country', blank=True, to='utils.Country', null=True)),
            ],
            options={
                'verbose_name': 'Unit',
                'verbose_name_plural': 'Units',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='UnitLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.PositiveSmallIntegerField(verbose_name='Level', choices=[(1, 'First level'), (2, 'Second level'), (3, 'Third level')])),
                ('institution', models.ForeignKey(to='institution.Institution', null=True)),
                ('unit', models.ForeignKey(verbose_name='Unit', to='institution.Unit', null=True)),
            ],
            options={
                'verbose_name': 'Hierarchical level',
                'verbose_name_plural': 'Hierarchical levels',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url_type', models.CharField(max_length=75, verbose_name='Type', choices=[(b'main', 'Main'), (b'other', 'Other')])),
                ('url', models.URLField(max_length=300, verbose_name='URL')),
                ('institution', models.ForeignKey(to='institution.Institution', null=True)),
            ],
            options={
                'verbose_name': 'URL',
                'verbose_name_plural': 'URLs',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.AddField(
            model_name='contactphone',
            name='institution',
            field=models.ForeignKey(to='institution.Institution', null=True),
        ),
        migrations.AddField(
            model_name='contactperson',
            name='institution',
            field=models.ForeignKey(to='institution.Institution', null=True),
        ),
        migrations.AddField(
            model_name='contactemail',
            name='institution',
            field=models.ForeignKey(to='institution.Institution', null=True),
        ),
        migrations.AddField(
            model_name='adm',
            name='institution',
            field=models.ForeignKey(to='institution.Institution', null=True),
        ),
    ]
