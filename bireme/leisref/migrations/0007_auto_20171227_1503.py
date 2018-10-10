# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leisref', '0006_auto_20170804_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='updated', null=True)),
                ('acronym', models.CharField(max_length=55, verbose_name='Acronym')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Database',
                'verbose_name_plural': 'Databases',
            },
        ),
        migrations.CreateModel(
            name='DatabaseLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language', choices=[(b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('database', models.ForeignKey(verbose_name='Database', to='leisref.Database')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
            },
        ),
        migrations.AlterField(
            model_name='act',
            name='act_collection',
            field=models.ForeignKey(verbose_name='Collection', blank=True, to='leisref.ActCollection', null=True),
        ),
        migrations.AlterField(
            model_name='actcity',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actcitylocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actcollection',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actcollectionlocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actcountryregion',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actcountryregionlocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actorganissuer',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actorganissuerlocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actrelationtype',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actrelationtypelocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actscope',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actscopelocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actsource',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actsourcelocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actstate',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='actstatelocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='acttype',
            name='language',
            field=models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='acttypelocal',
            name='language',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AlterField(
            model_name='acturl',
            name='language',
            field=models.CharField(blank=True, max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
        migrations.AddField(
            model_name='act',
            name='indexed_database',
            field=models.ManyToManyField(to='leisref.Database', verbose_name='Indexed in', blank=True),
        ),
    ]
