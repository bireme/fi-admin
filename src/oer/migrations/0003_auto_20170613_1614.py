# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oer', '0002_auto_20170529_1613'),
    ]

    operations = [
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('name', models.CharField(max_length=115, verbose_name='Name')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'verbose_name': 'Structure',
                'verbose_name_plural': 'Structures',
            },
        ),
        migrations.CreateModel(
            name='StructureLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('structure', models.ForeignKey(verbose_name='Structure', to='oer.Structure', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.AlterField(
            model_name='oer',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (1, 'Published'), (2, 'Refused'), (3, 'Deleted')]),
        ),
        migrations.AddField(
            model_name='oer',
            name='structure',
            field=models.ForeignKey(verbose_name='Structure', blank=True, to='oer.Structure', null=True, on_delete=models.PROTECT),
        ),
    ]
