# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oer', '0003_auto_20170613_1614'),
    ]

    operations = [
        migrations.CreateModel(
            name='InteractivityLevel',
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
                'verbose_name': 'Interactivity level',
                'verbose_name_plural': 'Interactivity levels',
            },
        ),
        migrations.CreateModel(
            name='InteractivityLevelLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')])),
                ('name', models.CharField(max_length=115, verbose_name='name')),
                ('interactivitylevel', models.ForeignKey(verbose_name='Interactivity level', to='oer.InteractivityLevel', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.AddField(
            model_name='oer',
            name='interactivity_level',
            field=models.ForeignKey(verbose_name='Interactivity level', blank=True, to='oer.InteractivityLevel', null=True, on_delete=models.PROTECT),
        ),
    ]
