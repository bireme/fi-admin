# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('title', '0006_auto_20160623_1204'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('collection', models.TextField(help_text='Enter one per line', verbose_name='Collection', blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Collection',
                'verbose_name_plural': 'Collections',
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('treatment_level', models.CharField(max_length=55, verbose_name='Treatment level', blank=True)),
                ('cooperative_center_code', models.CharField(max_length=55, verbose_name='Cooperative center', blank=True)),
                ('year', models.CharField(max_length=255, verbose_name='Year')),
                ('volume', models.CharField(max_length=255, verbose_name='Volume', blank=True)),
                ('number', models.CharField(max_length=55, verbose_name='Number', blank=True)),
                ('copies', models.CharField(max_length=55, verbose_name='Number of copies', blank=True)),
                ('status', models.CharField(max_length=55, verbose_name='Status (P/A)', choices=[(b'P', 'Present'), (b'A', 'Absent')])),
                ('publication_type', models.CharField(blank=True, max_length=55, verbose_name='Publication type', choices=[(b'S', 'Supplement'), (b'NE', 'Special number')])),
                ('notes', models.TextField(help_text='Enter one per line', verbose_name='Notes', blank=True)),
                ('urls', models.TextField(help_text='Enter one per line', verbose_name='URLs', blank=True)),
                ('classification', models.CharField(max_length=55, verbose_name='Classification', blank=True)),
                ('creation_date', models.CharField(help_text=b'Format: YYYYMMDD', max_length=55, verbose_name='Creation date', blank=True)),
                ('last_change_date', models.CharField(help_text=b'Format: YYYYMMDD', max_length=55, verbose_name='Last change date', blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-classification'],
                'verbose_name': 'Issue',
                'verbose_name_plural': 'Issues',
            },
        ),
        migrations.CreateModel(
            name='Mask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('mask', models.CharField(max_length=55, verbose_name='Mask code', blank=True)),
                ('frequency', models.CharField(blank=True, max_length=55, verbose_name='Frequency', choices=[(b'A', 'Annual'), (b'B', 'Bimonthly (every two months)'), (b'C', 'Biweekly (twice per week)'), (b'D', 'Daily'), (b'E', 'Fortnightly (every two weeks)'), (b'F', 'Semiannual/Biannual'), (b'G', 'Biennial (every two years)'), (b'H', 'Triennial (every three years)'), (b'I', 'Three times a week'), (b'J', 'Three times a month'), (b'K', 'Irregular'), (b'M', 'Monthly'), (b'Q', 'Quarterly (four times a year)'), (b'S', 'Semimonthly (twice per month)'), (b'T', 'Triannual (three times a year)'), (b'U', 'Continuously updated'), (b'W', 'Weekly'), (b'Z', 'Other frequencies'), (b'?', 'Unknown frequency')])),
                ('volumes', models.CharField(max_length=55, verbose_name='Volumes', blank=True)),
                ('issues', models.CharField(max_length=55, verbose_name='Issues', blank=True)),
                ('ascending', models.BooleanField(default=False, verbose_name='Ascending')),
                ('dummy', models.BooleanField(default=False, verbose_name='Dummy')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['mask'],
                'verbose_name': 'Mask',
                'verbose_name_plural': 'Masks',
            },
        ),
        migrations.AlterModelOptions(
            name='ownerlist',
            options={'verbose_name': 'Owners List', 'verbose_name_plural': 'Owners List'},
        ),
        migrations.AlterField(
            model_name='indexrange',
            name='copy',
            field=models.CharField(blank=True, max_length=55, verbose_name='Copy', choices=[(b'MI', 'MEDLINE Index'), (b'MR', 'MEDLINE Record')]),
        ),
        migrations.AlterField(
            model_name='title',
            name='frequency',
            field=models.CharField(blank=True, max_length=55, verbose_name='Frequency', choices=[(b'A', 'Annual'), (b'B', 'Bimonthly (every two months)'), (b'C', 'Biweekly (twice per week)'), (b'D', 'Daily'), (b'E', 'Fortnightly (every two weeks)'), (b'F', 'Semiannual/Biannual'), (b'G', 'Biennial (every two years)'), (b'H', 'Triennial (every three years)'), (b'I', 'Three times a week'), (b'J', 'Three times a month'), (b'K', 'Irregular'), (b'M', 'Monthly'), (b'Q', 'Quarterly (four times a year)'), (b'S', 'Semimonthly (twice per month)'), (b'T', 'Triannual (three times a year)'), (b'U', 'Continuously updated'), (b'W', 'Weekly'), (b'Z', 'Other frequencies'), (b'?', 'Unknown frequency')]),
        ),
        migrations.AlterField(
            model_name='title',
            name='treatment_level',
            field=models.CharField(default=b'K', max_length=55, verbose_name='Treatment level'),
        ),
        migrations.AddField(
            model_name='issue',
            name='mask',
            field=models.ForeignKey(related_name='+', verbose_name='Mask code', blank=True, to='title.Mask', null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='title',
            field=models.ForeignKey(verbose_name='Title', blank=True, to='title.Title'),
        ),
        migrations.AddField(
            model_name='issue',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='title',
            field=models.ForeignKey(verbose_name='Title', blank=True, to='title.Title'),
        ),
        migrations.AddField(
            model_name='collection',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
